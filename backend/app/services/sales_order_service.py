"""Sales order workflows and convert-to-bill (BIZ-52)."""

from datetime import date

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.role import ROLE_BILLING_USER
from app.models.sales_order import (
    STATUS_CANCELLED,
    STATUS_CONVERTED,
    STATUS_DRAFT,
    STATUS_TRANSITIONS,
    SalesOrder,
    SalesOrderItem,
)
from app.repositories.customer_repository import CustomerRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.sales_order_repository import SalesOrderRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.bill_service import BillService
from app.services.module_service import ModuleService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import calculate_bill_totals, money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "sales_orders"


class SalesOrderService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage sales orders")
        return ctx

    @staticmethod
    def serialize(row: SalesOrder) -> dict:
        return {
            "id": row.id,
            "order_number": row.order_number,
            "status": row.status,
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "notes": row.notes,
            "expected_delivery_date": (
                row.expected_delivery_date.isoformat() if row.expected_delivery_date else None
            ),
            "discount": float(row.discount),
            "subtotal": float(row.subtotal),
            "taxable_amount": float(row.taxable_amount),
            "cgst_amount": float(row.cgst_amount),
            "sgst_amount": float(row.sgst_amount),
            "gst_amount": float(row.gst_amount),
            "grand_total": float(row.grand_total),
            "bill_id": row.bill_id,
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
                    "unit_price": float(line.unit_price),
                    "gst_percentage": float(line.gst_percentage),
                    "discount": float(line.discount),
                    "taxable_amount": float(line.taxable_amount),
                    "cgst_amount": float(line.cgst_amount),
                    "sgst_amount": float(line.sgst_amount),
                    "total": float(line.total),
                    "uom": line.uom,
                }
                for line in (row.items or [])
            ],
        }

    @staticmethod
    def list_orders(*, status=None, page=1, per_page=100):
        ctx = SalesOrderService._require(write=False)
        rows, total = SalesOrderRepository.list_for_tenant(
            ctx.tenant_id, status=status, page=page, per_page=per_page
        )
        return (
            [SalesOrderService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get(order_id: str):
        ctx = SalesOrderService._require(write=False)
        row = SalesOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if row is None:
            raise NotFoundError("Sales order not found")
        return SalesOrderService.serialize(row)

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
            unit_price = (
                money(raw["unit_price"])
                if raw.get("unit_price") is not None and str(raw.get("unit_price")).strip() != ""
                else money(item.price)
            )
            prepared.append(
                {
                    "item_id": item.id,
                    "item_name": item.name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "gst_percentage": money(item.gst_percentage),
                    "uom": getattr(item, "sale_uom", None) or item.uom or "pcs",
                }
            )
        return prepared

    @staticmethod
    def create(
        *,
        items: list[dict],
        customer_id=None,
        customer_name=None,
        customer_phone=None,
        notes=None,
        discount=0,
        expected_delivery_date=None,
    ):
        ctx = SalesOrderService._require(write=True)
        prepared = SalesOrderService._resolve_lines(ctx.tenant_id, items)
        try:
            calculated = calculate_bill_totals(prepared, discount)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        cust_id = (customer_id or "").strip() or None
        cust_name = (customer_name or "").strip() or None
        cust_phone = (customer_phone or "").strip() or None
        if cust_id:
            customer = CustomerRepository.get_by_id_and_tenant(cust_id, ctx.tenant_id)
            if customer is None:
                raise ValidationError("Customer not found")
            cust_name = cust_name or customer.name
            cust_phone = cust_phone or customer.phone_e164 or customer.phone_national

        until = None
        if expected_delivery_date:
            if isinstance(expected_delivery_date, date):
                until = expected_delivery_date
            else:
                until = date.fromisoformat(str(expected_delivery_date)[:10])

        sequence, number = SalesOrderRepository.allocate_number(ctx.tenant_id)
        row = SalesOrder(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            order_number=number,
            order_sequence=sequence,
            customer_id=cust_id,
            customer_name=cust_name,
            customer_phone=cust_phone,
            notes=(notes or "").strip() or None,
            expected_delivery_date=until,
            status=STATUS_DRAFT,
            discount=calculated["discount"],
            subtotal=calculated["subtotal"],
            taxable_amount=calculated["taxable_amount"],
            cgst_amount=calculated["cgst_amount"],
            sgst_amount=calculated["sgst_amount"],
            gst_amount=calculated["gst_amount"],
            grand_total=calculated["grand_total"],
            created_by=ctx.user_id,
        )
        SalesOrderRepository.add(row)
        db.session.flush()
        for source, line in zip(prepared, calculated["lines"]):
            db.session.add(
                SalesOrderItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    sales_order_id=row.id,
                    item_id=line["item_id"],
                    item_name=line["item_name"],
                    quantity=line["quantity"],
                    unit_price=line["unit_price"],
                    gst_percentage=line["gst_percentage"],
                    discount=line["discount"],
                    taxable_amount=line["taxable_amount"],
                    cgst_amount=line["cgst_amount"],
                    sgst_amount=line["sgst_amount"],
                    total=line["total"],
                    uom=source.get("uom"),
                )
            )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_SALES_ORDER",
            entity_type="SALES_ORDER",
            entity_id=row.id,
            new_data={
                "order_number": number,
                "grand_total": float(calculated["grand_total"]),
                "lines": len(calculated["lines"]),
            },
        )
        db.session.commit()
        return SalesOrderService.serialize(SalesOrderRepository.get_by_id(ctx.tenant_id, row.id))

    @staticmethod
    def update_status(order_id: str, *, status: str, notes=None):
        ctx = SalesOrderService._require(write=True)
        row = SalesOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if row is None:
            raise NotFoundError("Sales order not found")
        next_status = (status or "").strip().upper()
        if next_status not in STATUS_TRANSITIONS.get(row.status, set()):
            raise ValidationError(f"Cannot change status from {row.status} to {next_status}")
        if next_status == STATUS_CONVERTED:
            raise ValidationError("Use convert endpoint to create a bill from a sales order")
        previous = row.status
        row.status = next_status
        if notes is not None:
            row.notes = (notes or "").strip() or None
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_SALES_ORDER_STATUS",
            entity_type="SALES_ORDER",
            entity_id=row.id,
            old_data={"status": previous},
            new_data={"status": next_status},
        )
        db.session.commit()
        return SalesOrderService.serialize(row)

    @staticmethod
    def convert_to_bill(order_id: str, *, payment_method=None):
        ctx = SalesOrderService._require(write=True)
        row = SalesOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if row is None:
            raise NotFoundError("Sales order not found")
        if row.status in {STATUS_CONVERTED, STATUS_CANCELLED}:
            raise ValidationError(f"Cannot convert a {row.status} sales order")
        if not row.items:
            raise ValidationError("Sales order has no line items")
        missing = [line for line in row.items if not line.item_id]
        if missing:
            raise ValidationError("Sales order lines must reference catalog items to convert")

        bill = BillService.create_bill(
            items=[
                {"item_id": line.item_id, "quantity": float(line.quantity)}
                for line in row.items
            ],
            discount=float(row.discount or 0),
            reference=row.order_number,
            payment_method=payment_method,
            customer_name=row.customer_name,
            customer_id=row.customer_id,
        )
        bill_id = bill["id"] if isinstance(bill, dict) else bill.id
        row = SalesOrderRepository.get_by_id(ctx.tenant_id, order_id)
        row.status = STATUS_CONVERTED
        row.bill_id = bill_id
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CONVERT_SALES_ORDER",
            entity_type="SALES_ORDER",
            entity_id=row.id,
            new_data={
                "order_number": row.order_number,
                "bill_id": row.bill_id,
                "status": STATUS_CONVERTED,
            },
        )
        db.session.commit()
        return {
            "sales_order": SalesOrderService.serialize(row),
            "bill": bill if isinstance(bill, dict) else BillService.serialize(bill),
        }
