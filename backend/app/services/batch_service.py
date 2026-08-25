"""Item batch receive, adjust, expiry listing, FEFO (BIZ-22)."""

from datetime import date, timedelta
from decimal import Decimal

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK
from app.extensions import db
from app.models.item_batch import ItemBatch
from app.repositories.item_batch_repository import ItemBatchRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.services.stock_movement_service import StockMovementService
from app.utils.exceptions import ConflictError, InsufficientStockError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

TYPE_BATCH_EXPIRING = "BATCH_EXPIRING"
TYPE_BATCH_EXPIRED = "BATCH_EXPIRED"
DEFAULT_EXPIRY_WARNING_DAYS = 7


class BatchService:
    MODULE = "batch_expiry"

    @staticmethod
    def _require_module():
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, BatchService.MODULE)
        return ctx, tenant

    @staticmethod
    def serialize(batch: ItemBatch, *, item_name: str | None = None) -> dict:
        today = date.today()
        expiry = batch.expiry_date
        days_left = None
        status = "ok"
        if expiry is not None:
            days_left = (expiry - today).days
            if days_left < 0:
                status = "expired"
            elif days_left <= DEFAULT_EXPIRY_WARNING_DAYS:
                status = "expiring"
        return {
            "id": batch.id,
            "item_id": batch.item_id,
            "item_name": item_name or (batch.item.name if batch.item else None),
            "batch_code": batch.batch_code,
            "expiry_date": expiry.isoformat() if expiry else None,
            "quantity": float(batch.quantity),
            "is_active": batch.is_active,
            "status": status,
            "days_until_expiry": days_left,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "updated_at": batch.updated_at.isoformat() if batch.updated_at else None,
        }

    @staticmethod
    def list_batches(*, item_id=None, status=None, within_days=None, page=1, per_page=50):
        require_permission(PERM_ITEMS_READ)
        ctx, _ = BatchService._require_module()
        rows, total = ItemBatchRepository.list_for_tenant(
            ctx.tenant_id,
            item_id=item_id,
            status=status,
            within_days=within_days,
            page=page,
            per_page=per_page,
        )
        return (
            [BatchService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def expiry_report(*, within_days: int = DEFAULT_EXPIRY_WARNING_DAYS, page=1, per_page=50):
        """Near-expiry + expired batches for grocery ops."""
        require_permission(PERM_ITEMS_READ)
        ctx, _ = BatchService._require_module()
        days = max(int(within_days or DEFAULT_EXPIRY_WARNING_DAYS), 0)
        expired, expired_total = ItemBatchRepository.list_for_tenant(
            ctx.tenant_id, status="expired", page=1, per_page=200
        )
        expiring, expiring_total = ItemBatchRepository.list_for_tenant(
            ctx.tenant_id,
            status="expiring",
            within_days=days,
            page=page,
            per_page=per_page,
        )
        return {
            "within_days": days,
            "expired": [BatchService.serialize(row) for row in expired],
            "expiring": [BatchService.serialize(row) for row in expiring],
            "summary": {
                "expired_count": expired_total,
                "expiring_count": expiring_total,
            },
        }

    @staticmethod
    def _notify_expiring(tenant_id: str, batches: list[ItemBatch]):
        for batch in batches:
            if batch.expiry_date is None:
                continue
            days_left = (batch.expiry_date - date.today()).days
            name = batch.item.name if batch.item else "Item"
            code = batch.batch_code or batch.id[:8]
            if days_left < 0:
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_BATCH_EXPIRED,
                    title=f"Expired batch: {name}",
                    message=f"Batch {code} expired on {batch.expiry_date.isoformat()} "
                    f"(qty {float(batch.quantity):g}).",
                    entity_type="ITEM_BATCH",
                    entity_id=batch.id,
                )
            elif days_left <= DEFAULT_EXPIRY_WARNING_DAYS:
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_BATCH_EXPIRING,
                    title=f"Expiring soon: {name}",
                    message=f"Batch {code} expires on {batch.expiry_date.isoformat()} "
                    f"({days_left} day(s) left, qty {float(batch.quantity):g}).",
                    entity_type="ITEM_BATCH",
                    entity_id=batch.id,
                )
        db.session.flush()

    @staticmethod
    def create_batch(*, item_id: str, quantity, expiry_date: date, batch_code=None, reason=None):
        require_permission(PERM_ITEMS_STOCK)
        ctx, _ = BatchService._require_module()
        item = ItemRepository.lock_by_id_and_tenant(item_id.strip(), ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        if not item.tracks_batches:
            raise ValidationError(
                "Enable 'tracks batches' on this item before receiving batch stock."
            )

        amount = qty(quantity)
        if amount <= 0:
            raise ValidationError("Quantity must be greater than zero")
        if expiry_date is None:
            raise ValidationError("expiry_date is required")

        code = (batch_code or "").strip() or None
        if code:
            existing = ItemBatchRepository.find_by_code(ctx.tenant_id, item.id, code)
            if existing:
                raise ConflictError("Batch code already exists for this item")

        previous = Decimal(item.stock_quantity) if item.stock_quantity is not None else Decimal("0")
        new_stock = previous + amount
        item.stock_quantity = new_stock

        batch = ItemBatch(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            batch_code=code,
            expiry_date=expiry_date,
            quantity=amount,
            is_active=True,
        )
        ItemBatchRepository.add(batch)

        reason_text = (reason or "").strip() or f"Batch receive {code or batch.id[:8]}"
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_BATCH",
            entity_type="ITEM_BATCH",
            entity_id=batch.id,
            new_data={
                **BatchService.serialize(batch, item_name=item.name),
                "stock_quantity": float(new_stock),
            },
        )
        StockMovementService.record(
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            delta=amount,
            quantity_after=new_stock,
            source="RECEIVE",
            reason=reason_text,
            reference_type="ITEM_BATCH",
            reference_id=batch.id,
            created_by=ctx.user_id,
        )
        NotificationService.notify_stock_transition(
            tenant_id=ctx.tenant_id,
            item=item,
            previous=previous,
            new_stock=new_stock,
        )
        if expiry_date <= date.today() + timedelta(days=DEFAULT_EXPIRY_WARNING_DAYS):
            BatchService._notify_expiring(ctx.tenant_id, [batch])

        db.session.commit()
        return BatchService.serialize(batch, item_name=item.name)

    @staticmethod
    def adjust_batch(batch_id: str, *, delta, reason: str):
        require_permission(PERM_ITEMS_STOCK)
        ctx, _ = BatchService._require_module()
        reason_text = (reason or "").strip()
        if not reason_text:
            raise ValidationError("Adjustment reason is required")

        batch = ItemBatchRepository.get_by_id(ctx.tenant_id, batch_id)
        if batch is None or not batch.is_active:
            raise NotFoundError("Batch not found")

        change = qty(delta)
        if change == 0:
            raise ValidationError("Adjustment amount cannot be zero")

        item = ItemRepository.lock_by_id_and_tenant(batch.item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")

        prev_batch_qty = Decimal(batch.quantity)
        new_batch_qty = prev_batch_qty + change
        if new_batch_qty < 0:
            raise ValidationError(
                f"Insufficient batch stock. Available: {float(prev_batch_qty):g}."
            )

        previous_item = (
            Decimal(item.stock_quantity) if item.stock_quantity is not None else Decimal("0")
        )
        new_item_stock = previous_item + change
        if new_item_stock < 0:
            raise ValidationError(
                f"Insufficient item stock. Available: {float(previous_item):g}."
            )

        batch.quantity = new_batch_qty
        if new_batch_qty == 0:
            batch.is_active = False
        item.stock_quantity = new_item_stock

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="ADJUST_BATCH",
            entity_type="ITEM_BATCH",
            entity_id=batch.id,
            old_data={"quantity": float(prev_batch_qty), "item_stock": float(previous_item)},
            new_data={
                "quantity": float(new_batch_qty),
                "item_stock": float(new_item_stock),
                "delta": float(change),
                "reason": reason_text,
            },
        )
        StockMovementService.record(
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            delta=change,
            quantity_after=new_item_stock,
            source="ADJUST",
            reason=reason_text,
            reference_type="ITEM_BATCH",
            reference_id=batch.id,
            created_by=ctx.user_id,
        )
        NotificationService.notify_stock_transition(
            tenant_id=ctx.tenant_id,
            item=item,
            previous=previous_item,
            new_stock=new_item_stock,
        )
        db.session.commit()
        return BatchService.serialize(batch, item_name=item.name)

    @staticmethod
    def assert_sellable_and_allocate(tenant_id: str, item, quantity: Decimal) -> list[tuple[ItemBatch, Decimal]]:
        """If item tracks batches with block policy, ensure sellable qty and FEFO-allocate."""
        if not getattr(item, "tracks_batches", False):
            return []
        if not getattr(item, "block_expired_batches", True):
            return []

        sellable = ItemBatchRepository.sellable_quantity(tenant_id, item.id)
        if quantity > sellable:
            raise InsufficientStockError(
                f"Insufficient sellable (non-expired) stock for {item.name}. "
                f"Available: {float(sellable):g}, requested: {float(quantity):g}.",
                details={
                    "item_id": item.id,
                    "item_name": item.name,
                    "available": float(sellable),
                    "requested": float(quantity),
                    "reason": "expired_batches_blocked",
                },
            )

        remaining = qty(quantity)
        allocations: list[tuple[ItemBatch, Decimal]] = []
        for batch in ItemBatchRepository.sellable_batches(tenant_id, item.id):
            if remaining <= 0:
                break
            take = min(Decimal(batch.quantity), remaining)
            if take <= 0:
                continue
            allocations.append((batch, take))
            remaining -= take
        return allocations

    @staticmethod
    def apply_allocations(allocations: list[tuple[ItemBatch, Decimal]]) -> None:
        for batch, take in allocations:
            batch.quantity = Decimal(batch.quantity) - take
            if batch.quantity <= 0:
                batch.quantity = Decimal("0")
                batch.is_active = False
