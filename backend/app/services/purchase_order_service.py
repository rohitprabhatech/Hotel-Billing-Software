"""Purchase order workflows and convert-to-purchase (BIZ-52)."""

from datetime import date
from decimal import Decimal

from app.constants.permissions import PERM_PURCHASES_READ, PERM_PURCHASES_WRITE
from app.extensions import db
from app.models.purchase_order import (
    STATUS_CANCELLED,
    STATUS_CONVERTED,
    STATUS_DRAFT,
    STATUS_TRANSITIONS,
    PurchaseOrder,
    PurchaseOrderItem,
)
from app.models.role import ROLE_BILLING_USER
from app.repositories.item_repository import ItemRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.supplier_repository import SupplierRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.purchase_service import PurchaseService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "purchase_orders"


class PurchaseOrderService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_PURCHASES_WRITE if write else PERM_PURCHASES_READ)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage purchase orders")
        return ctx

    @staticmethod
    def serialize(row: PurchaseOrder) -> dict:
        return {
            "id": row.id,
            "order_number": row.order_number,
            "status": row.status,
            "supplier_id": row.supplier_id,
            "supplier_name": row.supplier_name,
            "notes": row.notes,
            "expected_date": row.expected_date.isoformat() if row.expected_date else None,
            "subtotal": float(row.subtotal),
            "grand_total": float(row.grand_total),
            "purchase_id": row.purchase_id,
            "created_by": row.created_by,
            "created_by_name": row.creator.name if row.creator else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "items": [
                {
                    "id": line.id,
                    "item_id": line.item_id,
                    "item_name": line.item_name,
                    "quantity": float(line.quantity),
                    "unit_cost": float(line.unit_cost),
                    "line_total": float(line.line_total),
                    "uom": line.uom,
                }
                for line in (row.items or [])
            ],
        }

    @staticmethod
    def list_orders(*, status=None, page=1, per_page=100):
        ctx = PurchaseOrderService._require(write=False)
        rows, total = PurchaseOrderRepository.list_for_tenant(
            ctx.tenant_id, status=status, page=page, per_page=per_page
        )
        return (
            [PurchaseOrderService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get(order_id: str):
        ctx = PurchaseOrderService._require(write=False)
        row = PurchaseOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if row is None:
            raise NotFoundError("Purchase order not found")
        return PurchaseOrderService.serialize(row)

    @staticmethod
    def _resolve_lines(tenant_id: str, items: list[dict]) -> list[dict]:
        if not items:
            raise ValidationError("At least one line item is required")
        prepared = []
        for raw in items:
            item_id = (raw.get("item_id") or "").strip()
            if not item_id:
                raise ValidationError("item_id is required on each line")
            item = ItemRepository.get_by_id_and_tenant(item_id, tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item not found: {item_id}")
            quantity = qty(raw.get("quantity"))
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero")
            unit_cost = money(raw.get("unit_cost"))
            if unit_cost < 0:
                raise ValidationError("unit_cost cannot be negative")
            prepared.append(
                {
                    "item_id": item.id,
                    "item_name": item.name,
                    "quantity": quantity,
                    "unit_cost": unit_cost,
                    "line_total": money(unit_cost * quantity),
                    "uom": item.uom or "pcs",
                }
            )
        return prepared

    @staticmethod
    def create(*, items: list[dict], supplier_id=None, notes=None, expected_date=None):
        ctx = PurchaseOrderService._require(write=True)
        prepared = PurchaseOrderService._resolve_lines(ctx.tenant_id, items)

        supplier = None
        supplier_name = None
        sid = (supplier_id or "").strip() or None
        if sid:
            supplier = SupplierRepository.get_by_id_and_tenant(sid, ctx.tenant_id)
            if supplier is None or not supplier.is_active:
                raise ValidationError("Supplier not found or inactive")
            supplier_name = supplier.name

        until = None
        if expected_date:
            if isinstance(expected_date, date):
                until = expected_date
            else:
                until = date.fromisoformat(str(expected_date)[:10])

        subtotal = money(sum((line["line_total"] for line in prepared), Decimal("0")))
        sequence, number = PurchaseOrderRepository.allocate_number(ctx.tenant_id)
        row = PurchaseOrder(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            order_number=number,
            order_sequence=sequence,
            supplier_id=sid,
            supplier_name=supplier_name,
            notes=(notes or "").strip() or None,
            expected_date=until,
            status=STATUS_DRAFT,
            subtotal=subtotal,
            grand_total=subtotal,
            created_by=ctx.user_id,
        )
        PurchaseOrderRepository.add(row)
        db.session.flush()
        for line in prepared:
            db.session.add(
                PurchaseOrderItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    purchase_order_id=row.id,
                    item_id=line["item_id"],
                    item_name=line["item_name"],
                    quantity=line["quantity"],
                    unit_cost=line["unit_cost"],
                    line_total=line["line_total"],
                    uom=line.get("uom"),
                )
            )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_PURCHASE_ORDER",
            entity_type="PURCHASE_ORDER",
            entity_id=row.id,
            new_data={
                "order_number": number,
                "grand_total": float(subtotal),
                "lines": len(prepared),
            },
        )
        db.session.commit()
        return PurchaseOrderService.serialize(
            PurchaseOrderRepository.get_by_id(ctx.tenant_id, row.id)
        )

    @staticmethod
    def update_status(order_id: str, *, status: str, notes=None):
        ctx = PurchaseOrderService._require(write=True)
        row = PurchaseOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if row is None:
            raise NotFoundError("Purchase order not found")
        next_status = (status or "").strip().upper()
        if next_status not in STATUS_TRANSITIONS.get(row.status, set()):
            raise ValidationError(f"Cannot change status from {row.status} to {next_status}")
        if next_status == STATUS_CONVERTED:
            raise ValidationError("Use convert endpoint to create a purchase from a purchase order")
        previous = row.status
        row.status = next_status
        if notes is not None:
            row.notes = (notes or "").strip() or None
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_PURCHASE_ORDER_STATUS",
            entity_type="PURCHASE_ORDER",
            entity_id=row.id,
            old_data={"status": previous},
            new_data={"status": next_status},
        )
        db.session.commit()
        return PurchaseOrderService.serialize(row)

    @staticmethod
    def convert_to_purchase(order_id: str, *, payment_method="cash", invoice_number=None):
        ctx = PurchaseOrderService._require(write=True)
        row = PurchaseOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if row is None:
            raise NotFoundError("Purchase order not found")
        if row.status in {STATUS_CONVERTED, STATUS_CANCELLED}:
            raise ValidationError(f"Cannot convert a {row.status} purchase order")
        if not row.items:
            raise ValidationError("Purchase order has no line items")
        missing = [line for line in row.items if not line.item_id]
        if missing:
            raise ValidationError("Purchase order lines must reference catalog items to convert")

        purchase = PurchaseService.create_purchase(
            supplier_id=row.supplier_id,
            invoice_number=invoice_number or row.order_number,
            notes=row.notes,
            payment_method=payment_method,
            items=[
                {
                    "item_id": line.item_id,
                    "quantity": float(line.quantity),
                    "unit_cost": float(line.unit_cost),
                }
                for line in row.items
            ],
        )
        purchase_id = purchase["id"] if isinstance(purchase, dict) else purchase.id
        row = PurchaseOrderRepository.get_by_id(ctx.tenant_id, order_id)
        row.status = STATUS_CONVERTED
        row.purchase_id = purchase_id
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CONVERT_PURCHASE_ORDER",
            entity_type="PURCHASE_ORDER",
            entity_id=row.id,
            new_data={
                "order_number": row.order_number,
                "purchase_id": row.purchase_id,
                "status": STATUS_CONVERTED,
            },
        )
        db.session.commit()
        return {
            "purchase_order": PurchaseOrderService.serialize(row),
            "purchase": purchase
            if isinstance(purchase, dict)
            else PurchaseService.serialize(purchase),
        }
