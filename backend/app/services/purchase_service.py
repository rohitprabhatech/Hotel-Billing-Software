"""Purchase recording — stock increase with supplier linkage and ledger."""

from decimal import Decimal, InvalidOperation

from app.constants.permissions import PERM_PURCHASES_READ, PERM_PURCHASES_WRITE
from app.extensions import db
from app.models.purchase import PURCHASE_CANCELLED, PURCHASE_FINALIZED, Purchase, PurchaseItem
from app.repositories.item_repository import ItemRepository
from app.repositories.purchase_repository import PurchaseRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import InsufficientStockError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive


class PurchaseService:
    @staticmethod
    def _parse_unit_cost(value) -> Decimal:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError("Invalid unit cost") from exc
        if amount < 0:
            raise ValidationError("Unit cost cannot be negative")
        return money(amount)

    @staticmethod
    def list_purchases(
        *,
        status=None,
        supplier_id=None,
        q=None,
        page=1,
        per_page=50,
    ):
        require_permission(PERM_PURCHASES_READ)
        ctx = require_request_context()
        rows, total = PurchaseRepository.list_by_tenant(
            ctx.tenant_id,
            status=status,
            supplier_id=supplier_id,
            q=q,
            page=page,
            per_page=per_page,
        )
        return (
            [PurchaseService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_purchase(purchase_id: str, *, include_items=True):
        require_permission(PERM_PURCHASES_READ)
        ctx = require_request_context()
        purchase = PurchaseRepository.get_by_id_and_tenant(purchase_id, ctx.tenant_id)
        if purchase is None:
            raise NotFoundError("Purchase not found")
        return PurchaseService.serialize(purchase, include_items=include_items)

    @staticmethod
    def create_purchase(
        *,
        supplier_id: str | None,
        invoice_number: str | None,
        notes: str | None,
        items: list[dict],
        payment_method: str | None = "cash",
    ):
        require_permission(PERM_PURCHASES_WRITE)
        ctx = require_request_context()
        if not items:
            raise ValidationError("At least one line item is required")

        method = (payment_method or "cash").strip().lower()
        if method not in {"cash", "online", "credit"}:
            raise ValidationError("Payment method must be cash, online, or credit")

        supplier = None
        supplier_name = None
        if supplier_id:
            supplier = SupplierRepository.get_by_id_and_tenant(supplier_id.strip(), ctx.tenant_id)
            if supplier is None or not supplier.is_active:
                raise ValidationError("Supplier not found or inactive")
            supplier_name = supplier.name
        if method == "credit" and supplier is None:
            raise ValidationError("Supplier is required for credit purchases")

        merged: dict[str, dict] = {}
        for row in items:
            item_id = (row.get("item_id") or "").strip()
            if not item_id:
                raise ValidationError("item_id is required for each line")
            try:
                quantity = qty(row.get("quantity"))
            except Exception as exc:
                raise ValidationError("Invalid quantity") from exc
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero")
            unit_cost = PurchaseService._parse_unit_cost(row.get("unit_cost"))
            if item_id in merged:
                prev = merged[item_id]
                prev_qty = Decimal(prev["quantity"])
                prev_total = Decimal(prev["unit_cost"]) * prev_qty
                new_total = unit_cost * quantity
                combined_qty = prev_qty + quantity
                merged[item_id] = {
                    "quantity": combined_qty,
                    "unit_cost": (prev_total + new_total) / combined_qty,
                }
            else:
                merged[item_id] = {"quantity": quantity, "unit_cost": unit_cost}

        locked = {}
        for item_id in sorted(merged.keys()):
            item = ItemRepository.lock_by_id_and_tenant(item_id, ctx.tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item is inactive or not found: {item_id}")
            locked[item_id] = item

        sequence, purchase_number = PurchaseRepository.allocate_purchase_number(ctx.tenant_id)
        purchase_id = new_uuid()
        total_amount = Decimal("0.00")
        line_rows: list[PurchaseItem] = []

        for item_id, line in merged.items():
            item = locked[item_id]
            quantity = Decimal(line["quantity"])
            unit_cost = money(line["unit_cost"])
            line_total = money(unit_cost * quantity)
            total_amount += line_total
            line_rows.append(
                PurchaseItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    purchase_id=purchase_id,
                    item_id=item.id,
                    item_name=item.name,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    line_total=line_total,
                )
            )

        purchase = Purchase(
            id=purchase_id,
            tenant_id=ctx.tenant_id,
            purchase_number=purchase_number,
            purchase_sequence=sequence,
            supplier_id=supplier.id if supplier else None,
            supplier_name=supplier_name,
            invoice_number=(invoice_number or "").strip() or None,
            notes=(notes or "").strip() or None,
            total_amount=money(total_amount),
            status=PURCHASE_FINALIZED,
            created_by=ctx.user_id,
        )
        PurchaseRepository.add_purchase(purchase)
        for line in line_rows:
            PurchaseRepository.add_item(line)

        from app.services.notification_service import NotificationService
        from app.services.stock_movement_service import StockMovementService

        for line in line_rows:
            item = locked[line.item_id]
            quantity = Decimal(line.quantity)
            previous = (
                Decimal(item.stock_quantity) if item.stock_quantity is not None else None
            )
            new_stock = quantity if previous is None else (previous + quantity)
            item.stock_quantity = new_stock
            item.cost_price = line.unit_cost

            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=quantity,
                quantity_after=new_stock,
                source="PURCHASE",
                reason=f"Purchase {purchase_number}",
                reference_type="PURCHASE",
                reference_id=purchase.id,
                created_by=ctx.user_id,
            )
            from app.services.module_service import ModuleService
            from app.services.warehouse_service import WarehouseService

            tenant = TenantRepository.get_by_id(ctx.tenant_id)
            if WarehouseService.module_enabled(tenant):
                WarehouseService.receive_into_default(
                    tenant_id=ctx.tenant_id,
                    item_id=item.id,
                    quantity=quantity,
                )
            if previous is not None:
                NotificationService.notify_stock_transition(
                    tenant_id=ctx.tenant_id,
                    item=item,
                    previous=previous,
                    new_stock=new_stock,
                )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_PURCHASE",
            entity_type="PURCHASE",
            entity_id=purchase.id,
            new_data=PurchaseService.serialize(purchase, include_items=True),
        )
        if method == "credit" and supplier is not None:
            from app.services.party_ledger_service import PartyLedgerService

            PartyLedgerService.record_credit_purchase(
                tenant_id=ctx.tenant_id,
                supplier_id=supplier.id,
                amount=purchase.total_amount,
                purchase_id=purchase.id,
                purchase_number=purchase.purchase_number,
                created_by=ctx.user_id,
            )
        db.session.commit()
        db.session.refresh(purchase)
        return PurchaseService.serialize(purchase, include_items=True)

    @staticmethod
    def cancel_purchase(purchase_id: str, reason: str):
        require_permission(PERM_PURCHASES_WRITE)
        ctx = require_request_context()
        purchase = PurchaseRepository.get_by_id_and_tenant(purchase_id, ctx.tenant_id)
        if purchase is None:
            raise NotFoundError("Purchase not found")
        if purchase.status == PURCHASE_CANCELLED:
            raise ValidationError("Purchase is already cancelled")
        if purchase.status != PURCHASE_FINALIZED:
            raise ValidationError("Only finalized purchases can be cancelled")

        reason_text = (reason or "").strip()
        if not reason_text:
            raise ValidationError("Cancellation reason is required")

        old = PurchaseService.serialize(purchase, include_items=True)

        item_ids = sorted({line.item_id for line in purchase.items})
        locked = {
            item_id: ItemRepository.lock_by_id_and_tenant(item_id, ctx.tenant_id)
            for item_id in item_ids
        }
        for item_id, item in locked.items():
            if item is None:
                raise ValidationError(f"Item no longer exists: {item_id}")

        for line in purchase.items:
            item = locked[line.item_id]
            quantity = Decimal(line.quantity)
            if item.stock_quantity is None:
                raise ValidationError(
                    f"Cannot cancel purchase — item '{item.name}' no longer tracks stock"
                )
            previous = Decimal(item.stock_quantity)
            new_stock = previous - quantity
            if new_stock < 0:
                raise InsufficientStockError(
                    f"Cannot cancel purchase — insufficient stock for '{item.name}'. "
                    f"Available: {float(previous):g}, purchase qty: {float(quantity):g}."
                )

        from app.services.stock_movement_service import StockMovementService

        for line in purchase.items:
            item = locked[line.item_id]
            quantity = Decimal(line.quantity)
            previous = Decimal(item.stock_quantity)
            new_stock = previous - quantity
            item.stock_quantity = new_stock
            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=-quantity,
                quantity_after=new_stock,
                source="PURCHASE_CANCEL",
                reason=reason_text,
                reference_type="PURCHASE",
                reference_id=purchase.id,
                created_by=ctx.user_id,
            )
            from app.services.module_service import ModuleService
            from app.services.warehouse_service import WarehouseService

            tenant = TenantRepository.get_by_id(ctx.tenant_id)
            if WarehouseService.module_enabled(tenant):
                WarehouseService.adjust_warehouse_stock(
                    tenant_id=ctx.tenant_id,
                    warehouse_id=WarehouseService.ensure_default_warehouse(ctx.tenant_id).id,
                    item_id=item.id,
                    delta=-quantity,
                )

        purchase.status = PURCHASE_CANCELLED
        purchase.cancelled_by = ctx.user_id
        purchase.cancelled_at = utc_now_naive()
        purchase.cancellation_reason = reason_text

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CANCEL_PURCHASE",
            entity_type="PURCHASE",
            entity_id=purchase.id,
            old_data=old,
            new_data=PurchaseService.serialize(purchase, include_items=True),
        )
        if purchase.supplier_id:
            from app.services.party_ledger_service import PartyLedgerService

            PartyLedgerService.record_purchase_cancel_reversal(
                tenant_id=ctx.tenant_id,
                supplier_id=purchase.supplier_id,
                amount=purchase.total_amount,
                purchase_id=purchase.id,
                purchase_number=purchase.purchase_number,
                created_by=ctx.user_id,
                reason=reason_text,
            )
        db.session.commit()
        db.session.refresh(purchase)
        return PurchaseService.serialize(purchase, include_items=True)

    @staticmethod
    def serialize(purchase: Purchase, *, include_items=False):
        data = {
            "id": purchase.id,
            "purchase_number": purchase.purchase_number,
            "purchase_sequence": purchase.purchase_sequence,
            "supplier_id": purchase.supplier_id,
            "supplier_name": purchase.supplier_name,
            "invoice_number": purchase.invoice_number,
            "notes": purchase.notes,
            "total_amount": float(purchase.total_amount),
            "status": purchase.status,
            "created_by": purchase.created_by,
            "created_by_name": purchase.creator.name if purchase.creator else None,
            "created_at": purchase.created_at.isoformat() if purchase.created_at else None,
            "cancelled_by": purchase.cancelled_by,
            "cancelled_at": purchase.cancelled_at.isoformat() if purchase.cancelled_at else None,
            "cancellation_reason": purchase.cancellation_reason,
        }
        if include_items:
            data["items"] = [
                {
                    "id": line.id,
                    "item_id": line.item_id,
                    "item_name": line.item_name,
                    "quantity": float(line.quantity),
                    "unit_cost": float(line.unit_cost),
                    "line_total": float(line.line_total),
                }
                for line in (purchase.items or [])
            ]
        return data
