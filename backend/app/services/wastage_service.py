"""Food wastage business logic (BIZ-18)."""

from datetime import date
from decimal import Decimal

from app.constants.permissions import PERM_WASTAGE_READ, PERM_WASTAGE_WRITE
from app.extensions import db
from app.models.wastage import WastageEntry
from app.repositories.item_repository import ItemRepository
from app.repositories.wastage_repository import WastageRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import qty
from app.utils.periods import local_now, parse_date
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class WastageService:
    @staticmethod
    def _tenant_tz() -> str:
        ctx = require_request_context()
        return getattr(ctx, "tenant_timezone", None) or "Asia/Kolkata"

    @staticmethod
    def _parse_filter_date(value: str | None) -> date | None:
        if value is None or not str(value).strip():
            return None
        try:
            return parse_date(str(value).strip(), WastageService._tenant_tz()).date()
        except ValueError as exc:
            raise ValidationError("Dates must be YYYY-MM-DD") from exc

    @staticmethod
    def list_wastage(
        *,
        item_id=None,
        from_date=None,
        to_date=None,
        page=1,
        per_page=50,
    ):
        require_permission(PERM_WASTAGE_READ)
        ctx = require_request_context()
        date_from = WastageService._parse_filter_date(from_date)
        date_to = WastageService._parse_filter_date(to_date)
        if date_from and date_to and date_from > date_to:
            raise ValidationError("from date cannot be after to date")
        rows, total = WastageRepository.list_by_tenant(
            ctx.tenant_id,
            item_id=item_id,
            from_date=date_from,
            to_date=date_to,
            page=page,
            per_page=per_page,
        )
        return (
            [WastageService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_wastage(wastage_id: str):
        require_permission(PERM_WASTAGE_READ)
        ctx = require_request_context()
        row = WastageRepository.get_by_id_and_tenant(wastage_id, ctx.tenant_id)
        if row is None:
            raise NotFoundError("Wastage entry not found")
        return WastageService.serialize(row)

    @staticmethod
    def create_wastage(
        *,
        item_id: str,
        quantity,
        reason: str | None = None,
        category: str | None = None,
        wastage_date=None,
    ):
        require_permission(PERM_WASTAGE_WRITE)
        ctx = require_request_context()
        parsed_item_id = (item_id or "").strip()
        if not parsed_item_id:
            raise ValidationError("item_id is required")
        parsed_qty = qty(quantity)
        if parsed_qty <= 0:
            raise ValidationError("Quantity must be greater than zero")

        item = ItemRepository.lock_by_id_and_tenant(parsed_item_id, ctx.tenant_id)
        if item is None or not item.is_active:
            raise ValidationError("Item not found or inactive")
        if item.stock_quantity is None:
            raise ValidationError(
                "This item does not track stock. Enable stock tracking before logging wastage."
            )

        previous = Decimal(item.stock_quantity)
        delta = -parsed_qty
        new_stock = previous + delta
        if new_stock < 0:
            raise ValidationError(
                f"Insufficient stock. Available: {float(previous):g}, wastage: {float(parsed_qty):g}."
            )

        from app.services.batch_service import BatchService

        batch_allocations = BatchService.allocate_for_writeoff(
            ctx.tenant_id, item, parsed_qty
        )

        tz = WastageService._tenant_tz()
        if wastage_date:
            entry_date = wastage_date
            if isinstance(entry_date, str):
                entry_date = parse_date(entry_date, tz).date()
        else:
            entry_date = local_now(tz).date()

        reason_text = (reason or "").strip() or None
        category_text = (category or "").strip()[:80] or None
        entry_id = new_uuid()
        from app.services.stock_movement_service import StockMovementService

        movement = StockMovementService.record(
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            delta=delta,
            quantity_after=new_stock,
            source="WASTAGE",
            reason=reason_text,
            reference_type="WASTAGE",
            reference_id=entry_id,
            created_by=ctx.user_id,
        )
        item.stock_quantity = new_stock
        if batch_allocations:
            BatchService.apply_allocations(batch_allocations)

        entry = WastageEntry(
            id=entry_id,
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            item_name=item.name,
            quantity=parsed_qty,
            reason=reason_text,
            category=category_text,
            wastage_date=entry_date,
            stock_movement_id=movement.id,
            created_by=ctx.user_id,
        )
        WastageRepository.add(entry)
        serialized = WastageService.serialize(entry)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_WASTAGE",
            entity_type="WASTAGE",
            entity_id=entry.id,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def serialize(entry: WastageEntry):
        return {
            "id": entry.id,
            "item_id": entry.item_id,
            "item_name": entry.item_name,
            "quantity": float(entry.quantity),
            "reason": entry.reason,
            "category": entry.category,
            "wastage_date": entry.wastage_date.isoformat() if entry.wastage_date else None,
            "stock_movement_id": entry.stock_movement_id,
            "created_by": entry.created_by,
            "created_by_name": entry.creator.name if entry.creator else None,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }
