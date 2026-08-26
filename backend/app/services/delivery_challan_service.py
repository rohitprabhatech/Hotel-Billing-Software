"""Delivery challan workflows, PDF, convert-to-bill (BIZ-36)."""

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.delivery_challan import (
    STATUS_CANCELLED,
    STATUS_CONVERTED,
    STATUS_DRAFT,
    STATUS_TRANSITIONS,
    DeliveryChallan,
    DeliveryChallanItem,
)
from app.models.role import ROLE_BILLING_USER
from app.repositories.customer_repository import CustomerRepository
from app.repositories.delivery_challan_repository import DeliveryChallanRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.bill_service import BillService
from app.services.module_service import ModuleService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "delivery_challan"


class DeliveryChallanService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage delivery challans")
        return ctx

    @staticmethod
    def serialize(row: DeliveryChallan) -> dict:
        return {
            "id": row.id,
            "challan_number": row.challan_number,
            "status": row.status,
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "delivery_address": row.delivery_address,
            "vehicle_number": row.vehicle_number,
            "notes": row.notes,
            "quotation_id": row.quotation_id,
            "bill_id": row.bill_id,
            "transport_charge": float(getattr(row, "transport_charge", 0) or 0),
            "printed_count": int(row.printed_count or 0),
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
                    "unit_price": float(line.unit_price) if line.unit_price is not None else None,
                    "uom": line.uom,
                }
                for line in (row.items or [])
            ],
        }

    @staticmethod
    def list_challans(*, status=None, page=1, per_page=100):
        ctx = DeliveryChallanService._require(write=False)
        rows, total = DeliveryChallanRepository.list_for_tenant(
            ctx.tenant_id, status=status, page=page, per_page=per_page
        )
        return (
            [DeliveryChallanService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get(challan_id: str):
        ctx = DeliveryChallanService._require(write=False)
        row = DeliveryChallanRepository.get_by_id(ctx.tenant_id, challan_id)
        if row is None:
            raise NotFoundError("Delivery challan not found")
        return DeliveryChallanService.serialize(row)

    @staticmethod
    def get_entity(challan_id: str) -> DeliveryChallan:
        ctx = DeliveryChallanService._require(write=False)
        row = DeliveryChallanRepository.get_by_id(ctx.tenant_id, challan_id)
        if row is None:
            raise NotFoundError("Delivery challan not found")
        return row

    @staticmethod
    def create(
        *,
        items: list[dict],
        customer_id=None,
        customer_name=None,
        customer_phone=None,
        delivery_address=None,
        vehicle_number=None,
        notes=None,
        quotation_id=None,
        transport_charge=0,
    ):
        ctx = DeliveryChallanService._require(write=True)
        if not items:
            raise ValidationError("At least one line item is required")

        try:
            transport_value = money(transport_charge or 0)
        except Exception as exc:
            raise ValidationError("Invalid transport charge") from exc
        if transport_value < 0:
            raise ValidationError("Transport charge cannot be negative")
        if transport_value > 0:
            from app.services.module_service import ModuleService

            tenant = TenantRepository.get_by_id(ctx.tenant_id)
            if not ModuleService.is_enabled_for_tenant(tenant, "transport_charges"):
                raise ValidationError("Transport charges are not enabled for this business")

        quote_id = (quotation_id or "").strip() or None
        if quote_id:
            quote = QuotationRepository.get_by_id(ctx.tenant_id, quote_id)
            if quote is None:
                raise ValidationError("Quotation not found")

        cust_id = (customer_id or "").strip() or None
        cust_name = (customer_name or "").strip() or None
        cust_phone = (customer_phone or "").strip() or None
        if cust_id:
            customer = CustomerRepository.get_by_id_and_tenant(cust_id, ctx.tenant_id)
            if customer is None:
                raise ValidationError("Customer not found")
            cust_name = cust_name or customer.name
            cust_phone = cust_phone or customer.phone_e164 or customer.phone_national

        resolved = []
        for raw in items:
            item_id = (raw.get("item_id") or "").strip()
            if not item_id:
                raise ValidationError("item_id is required on each line")
            item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item not found: {item_id}")
            quantity = qty(raw.get("quantity"))
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero")
            unit_price = None
            if raw.get("unit_price") is not None and str(raw.get("unit_price")).strip() != "":
                unit_price = money(raw["unit_price"])
            resolved.append(
                {
                    "item_id": item.id,
                    "item_name": item.name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "uom": getattr(item, "sale_uom", None) or item.uom or "pcs",
                }
            )

        sequence, number = DeliveryChallanRepository.allocate_number(ctx.tenant_id)
        row = DeliveryChallan(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            challan_number=number,
            challan_sequence=sequence,
            customer_id=cust_id,
            customer_name=cust_name,
            customer_phone=cust_phone,
            delivery_address=(delivery_address or "").strip() or None,
            vehicle_number=(vehicle_number or "").strip() or None,
            notes=(notes or "").strip() or None,
            status=STATUS_DRAFT,
            quotation_id=quote_id,
            transport_charge=transport_value,
            created_by=ctx.user_id,
        )
        DeliveryChallanRepository.add(row)
        db.session.flush()
        for line in resolved:
            db.session.add(
                DeliveryChallanItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    challan_id=row.id,
                    item_id=line["item_id"],
                    item_name=line["item_name"],
                    quantity=line["quantity"],
                    unit_price=line["unit_price"],
                    uom=line["uom"],
                )
            )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_DELIVERY_CHALLAN",
            entity_type="DELIVERY_CHALLAN",
            entity_id=row.id,
            new_data={"challan_number": number, "lines": len(resolved)},
        )
        db.session.commit()
        return DeliveryChallanService.serialize(
            DeliveryChallanRepository.get_by_id(ctx.tenant_id, row.id)
        )

    @staticmethod
    def update_status(challan_id: str, *, status: str, notes=None):
        ctx = DeliveryChallanService._require(write=True)
        row = DeliveryChallanRepository.get_by_id(ctx.tenant_id, challan_id)
        if row is None:
            raise NotFoundError("Delivery challan not found")
        next_status = (status or "").strip().upper()
        if next_status not in STATUS_TRANSITIONS.get(row.status, set()):
            raise ValidationError(f"Cannot change status from {row.status} to {next_status}")
        if next_status == STATUS_CONVERTED:
            raise ValidationError("Use convert endpoint to create a bill from a challan")
        previous = row.status
        row.status = next_status
        if notes is not None:
            row.notes = (notes or "").strip() or None
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_DELIVERY_CHALLAN_STATUS",
            entity_type="DELIVERY_CHALLAN",
            entity_id=row.id,
            old_data={"status": previous},
            new_data={"status": next_status},
        )
        db.session.commit()
        return DeliveryChallanService.serialize(row)

    @staticmethod
    def convert_to_bill(challan_id: str, *, payment_method=None):
        ctx = DeliveryChallanService._require(write=True)
        row = DeliveryChallanRepository.get_by_id(ctx.tenant_id, challan_id)
        if row is None:
            raise NotFoundError("Delivery challan not found")
        if row.status in {STATUS_CONVERTED, STATUS_CANCELLED}:
            raise ValidationError(f"Cannot convert a {row.status} challan")
        if not row.items:
            raise ValidationError("Challan has no line items")
        if any(not line.item_id for line in row.items):
            raise ValidationError("Challan lines must reference catalog items to convert")

        bill = BillService.create_bill(
            items=[
                {"item_id": line.item_id, "quantity": float(line.quantity)}
                for line in row.items
            ],
            reference=row.challan_number,
            payment_method=payment_method,
            customer_name=row.customer_name,
            customer_id=row.customer_id,
            transport_charge=float(getattr(row, "transport_charge", 0) or 0),
        )
        bill_id = bill["id"] if isinstance(bill, dict) else bill.id
        row = DeliveryChallanRepository.get_by_id(ctx.tenant_id, challan_id)
        row.status = STATUS_CONVERTED
        row.bill_id = bill_id
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CONVERT_DELIVERY_CHALLAN",
            entity_type="DELIVERY_CHALLAN",
            entity_id=row.id,
            new_data={
                "challan_number": row.challan_number,
                "bill_id": row.bill_id,
                "status": STATUS_CONVERTED,
            },
        )
        db.session.commit()
        return {
            "challan": DeliveryChallanService.serialize(row),
            "bill": bill if isinstance(bill, dict) else BillService.serialize(bill),
        }

    @staticmethod
    def record_print(challan_id: str):
        ctx = DeliveryChallanService._require(write=False)
        row = DeliveryChallanRepository.get_by_id(ctx.tenant_id, challan_id)
        if row is None:
            raise NotFoundError("Delivery challan not found")
        row.printed_count = int(row.printed_count or 0) + 1
        db.session.commit()
        return DeliveryChallanService.serialize(row)
