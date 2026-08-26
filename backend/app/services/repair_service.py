"""Repair / service ticket workflows (BIZ-31)."""

from decimal import Decimal

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.repair_order import (
    ALLOWED_REPAIR_STATUSES,
    STATUS_DELIVERED,
    STATUS_READY,
    STATUS_RECEIVED,
    STATUS_TRANSITIONS,
    RepairOrder,
)
from app.models.role import ROLE_BILLING_USER
from app.repositories.item_repository import ItemRepository
from app.repositories.repair_order_repository import RepairOrderRepository
from app.repositories.serial_unit_repository import SerialUnitRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive

MODULE = "repair_service"


class RepairService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage repair tickets")
        return ctx

    @staticmethod
    def serialize(row: RepairOrder) -> dict:
        unit = row.serial_unit
        item = row.item
        return {
            "id": row.id,
            "repair_number": row.repair_number,
            "status": row.status,
            "serial_unit_id": row.serial_unit_id,
            "serial": unit.serial if unit else None,
            "item_id": row.item_id,
            "item_name": item.name if item else None,
            "bill_id": row.bill_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "issue_description": row.issue_description,
            "notes": row.notes,
            "estimated_charge": float(row.estimated_charge) if row.estimated_charge is not None else None,
            "delivered_at": row.delivered_at.isoformat() if row.delivered_at else None,
            "created_by": row.created_by,
            "created_by_name": row.creator.name if row.creator else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def list_orders(*, status=None, page=1, per_page=100):
        ctx = RepairService._require(write=False)
        rows, total = RepairOrderRepository.list_for_tenant(
            ctx.tenant_id, status=status, page=page, per_page=per_page
        )
        return (
            [RepairService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get_order(repair_id: str):
        ctx = RepairService._require(write=False)
        row = RepairOrderRepository.get_by_id(ctx.tenant_id, repair_id)
        if row is None:
            raise NotFoundError("Repair ticket not found")
        return RepairService.serialize(row)

    @staticmethod
    def create(
        *,
        serial_unit_id: str,
        issue_description: str,
        customer_name=None,
        customer_phone=None,
        bill_id=None,
        notes=None,
        estimated_charge=None,
    ):
        ctx = RepairService._require(write=True)
        issue = (issue_description or "").strip()
        if not issue:
            raise ValidationError("Issue description is required")
        unit = SerialUnitRepository.lock_by_id(ctx.tenant_id, serial_unit_id.strip())
        if unit is None:
            raise NotFoundError("Serial / IMEI unit not found")
        item = ItemRepository.get_by_id_and_tenant(unit.item_id, ctx.tenant_id)
        if item is None:
            raise ValidationError("Item not found for serial unit")
        if unit.status not in {"SOLD", "QUARANTINE", "IN_STOCK"}:
            raise ValidationError("Serial unit cannot be sent for repair in its current status")

        sequence, repair_number = RepairOrderRepository.allocate_number(ctx.tenant_id)
        charge = None
        if estimated_charge is not None and str(estimated_charge).strip() != "":
            charge = money(estimated_charge)

        row = RepairOrder(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            repair_number=repair_number,
            repair_sequence=sequence,
            serial_unit_id=unit.id,
            item_id=item.id,
            bill_id=(bill_id or "").strip() or unit.sold_bill_id,
            customer_name=(customer_name or "").strip() or None,
            customer_phone=(customer_phone or "").strip() or None,
            issue_description=issue,
            status=STATUS_RECEIVED,
            notes=(notes or "").strip() or None,
            estimated_charge=charge,
            created_by=ctx.user_id,
        )
        RepairOrderRepository.add(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_REPAIR",
            entity_type="REPAIR_ORDER",
            entity_id=row.id,
            new_data={
                "repair_number": repair_number,
                "serial": unit.serial,
                "item_name": item.name,
                "status": STATUS_RECEIVED,
            },
        )
        db.session.commit()
        db.session.refresh(row)
        return RepairService.serialize(row)

    @staticmethod
    def update_status(repair_id: str, *, status: str, notes=None):
        ctx = RepairService._require(write=True)
        row = RepairOrderRepository.get_by_id(ctx.tenant_id, repair_id)
        if row is None:
            raise NotFoundError("Repair ticket not found")
        new_status = (status or "").upper()
        if new_status not in ALLOWED_REPAIR_STATUSES:
            raise ValidationError("Invalid repair status")
        allowed = STATUS_TRANSITIONS.get(row.status, set())
        if new_status != row.status and new_status not in allowed:
            raise ValidationError(f"Cannot change status from {row.status} to {new_status}")
        old_status = row.status
        row.status = new_status
        if notes is not None:
            row.notes = (notes or "").strip() or None
        if new_status == STATUS_DELIVERED:
            row.delivered_at = utc_now_naive()
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_REPAIR_STATUS",
            entity_type="REPAIR_ORDER",
            entity_id=row.id,
            old_data={"status": old_status},
            new_data={"status": new_status},
        )
        if new_status == STATUS_READY and old_status != STATUS_READY:
            NotificationService.notify_repair_ready(
                tenant_id=ctx.tenant_id,
                repair_number=row.repair_number,
                serial=row.serial_unit.serial if row.serial_unit else "",
                user_id=ctx.user_id,
            )
        db.session.commit()
        db.session.refresh(row)
        return RepairService.serialize(row)
