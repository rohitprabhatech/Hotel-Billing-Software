"""Installation job workflows (BIZ-33)."""

from datetime import datetime

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.installation_order import (
    ALLOWED_INSTALLATION_STATUSES,
    STATUS_COMPLETED,
    STATUS_SCHEDULED,
    STATUS_TRANSITIONS,
    InstallationOrder,
)
from app.models.role import ROLE_BILLING_USER
from app.repositories.item_repository import ItemRepository
from app.repositories.installation_order_repository import InstallationOrderRepository
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

MODULE = "installation"


class InstallationService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage installation jobs")
        return ctx

    @staticmethod
    def _parse_scheduled_at(value) -> datetime | None:
        if value is None or str(value).strip() == "":
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value
        text = str(value).strip().replace("Z", "")
        try:
            if "T" in text:
                return datetime.fromisoformat(text)
            return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        except ValueError as exc:
            try:
                return datetime.strptime(text[:16], "%Y-%m-%dT%H:%M")
            except ValueError:
                raise ValidationError("scheduled_at must be a valid date/time") from exc

    @staticmethod
    def serialize(row: InstallationOrder) -> dict:
        unit = row.serial_unit
        item = row.item
        order = row.custom_order
        return {
            "id": row.id,
            "installation_number": row.installation_number,
            "status": row.status,
            "serial_unit_id": row.serial_unit_id,
            "serial": unit.serial if unit else None,
            "custom_order_id": row.custom_order_id,
            "custom_order_number": order.order_number if order else None,
            "custom_order_title": order.title if order else None,
            "item_id": row.item_id,
            "item_name": item.name if item else (order.title if order else None),
            "bill_id": row.bill_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "install_address": row.install_address,
            "scheduled_at": row.scheduled_at.isoformat() if row.scheduled_at else None,
            "technician_name": row.technician_name,
            "notes": row.notes,
            "estimated_charge": float(row.estimated_charge) if row.estimated_charge is not None else None,
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            "created_by": row.created_by,
            "created_by_name": row.creator.name if row.creator else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def list_orders(*, status=None, from_date=None, to_date=None, page=1, per_page=100):
        ctx = InstallationService._require(write=False)
        start = InstallationService._parse_scheduled_at(from_date) if from_date else None
        end = InstallationService._parse_scheduled_at(to_date) if to_date else None
        rows, total = InstallationOrderRepository.list_for_tenant(
            ctx.tenant_id,
            status=status,
            from_date=start,
            to_date=end,
            page=page,
            per_page=per_page,
        )
        return (
            [InstallationService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get_order(installation_id: str):
        ctx = InstallationService._require(write=False)
        row = InstallationOrderRepository.get_by_id(ctx.tenant_id, installation_id)
        if row is None:
            raise NotFoundError("Installation job not found")
        return InstallationService.serialize(row)

    @staticmethod
    def create(
        *,
        serial_unit_id=None,
        custom_order_id=None,
        scheduled_at=None,
        install_address=None,
        customer_name=None,
        customer_phone=None,
        bill_id=None,
        notes=None,
        technician_name=None,
        estimated_charge=None,
    ):
        ctx = InstallationService._require(write=True)
        schedule = InstallationService._parse_scheduled_at(scheduled_at)
        if schedule is None:
            raise ValidationError("Scheduled date/time is required")

        charge = None
        if estimated_charge is not None and str(estimated_charge).strip() != "":
            charge = money(estimated_charge)

        order_id = (custom_order_id or "").strip() or None
        serial_id = (serial_unit_id or "").strip() or None

        if order_id:
            from app.models.custom_order import ORDER_TYPE_FURNITURE, STATUS_DELIVERED, STATUS_READY
            from app.repositories.custom_order_repository import CustomOrderRepository

            order = CustomOrderRepository.get_by_id(ctx.tenant_id, order_id)
            if order is None:
                raise NotFoundError("Custom order not found")
            if order.order_type != ORDER_TYPE_FURNITURE:
                raise ValidationError("Only furniture custom orders can use this installation path")
            if order.status not in {STATUS_READY, STATUS_DELIVERED}:
                raise ValidationError("Custom order must be READY or DELIVERED before installation")

            sequence, installation_number = InstallationOrderRepository.allocate_number(ctx.tenant_id)
            row = InstallationOrder(
                id=new_uuid(),
                tenant_id=ctx.tenant_id,
                installation_number=installation_number,
                installation_sequence=sequence,
                serial_unit_id=None,
                custom_order_id=order.id,
                item_id=None,
                bill_id=order.bill_id,
                customer_name=(customer_name or "").strip() or order.customer_name,
                customer_phone=(customer_phone or "").strip() or order.customer_phone,
                install_address=(install_address or "").strip() or None,
                scheduled_at=schedule,
                status=STATUS_SCHEDULED,
                notes=(notes or "").strip() or None,
                technician_name=(technician_name or "").strip() or None,
                estimated_charge=charge,
                created_by=ctx.user_id,
            )
            InstallationOrderRepository.add(row)
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="CREATE_INSTALLATION",
                entity_type="INSTALLATION_ORDER",
                entity_id=row.id,
                new_data={
                    "installation_number": installation_number,
                    "custom_order_number": order.order_number,
                    "status": STATUS_SCHEDULED,
                    "scheduled_at": schedule.isoformat(),
                },
            )
            NotificationService.notify_installation_scheduled(
                tenant_id=ctx.tenant_id,
                installation_number=installation_number,
                serial=order.order_number,
                scheduled_at=schedule.isoformat(sep=" ", timespec="minutes"),
                user_id=ctx.user_id,
            )
            db.session.commit()
            db.session.refresh(row)
            return InstallationService.serialize(row)

        unit = SerialUnitRepository.lock_by_id(ctx.tenant_id, serial_id)
        if unit is None:
            raise NotFoundError("Serial / IMEI unit not found")
        item = ItemRepository.get_by_id_and_tenant(unit.item_id, ctx.tenant_id)
        if item is None:
            raise ValidationError("Item not found for serial unit")
        if unit.status not in {"SOLD", "IN_STOCK", "QUARANTINE"}:
            raise ValidationError("Serial unit cannot be scheduled for installation")

        sequence, installation_number = InstallationOrderRepository.allocate_number(ctx.tenant_id)

        row = InstallationOrder(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            installation_number=installation_number,
            installation_sequence=sequence,
            serial_unit_id=unit.id,
            custom_order_id=None,
            item_id=item.id,
            bill_id=(bill_id or "").strip() or unit.sold_bill_id,
            customer_name=(customer_name or "").strip() or None,
            customer_phone=(customer_phone or "").strip() or None,
            install_address=(install_address or "").strip() or None,
            scheduled_at=schedule,
            status=STATUS_SCHEDULED,
            notes=(notes or "").strip() or None,
            technician_name=(technician_name or "").strip() or None,
            estimated_charge=charge,
            created_by=ctx.user_id,
        )
        InstallationOrderRepository.add(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_INSTALLATION",
            entity_type="INSTALLATION_ORDER",
            entity_id=row.id,
            new_data={
                "installation_number": installation_number,
                "serial": unit.serial,
                "item_name": item.name,
                "status": STATUS_SCHEDULED,
                "scheduled_at": schedule.isoformat(),
            },
        )
        NotificationService.notify_installation_scheduled(
            tenant_id=ctx.tenant_id,
            installation_number=installation_number,
            serial=unit.serial,
            scheduled_at=schedule.isoformat(sep=" ", timespec="minutes"),
            user_id=ctx.user_id,
        )
        db.session.commit()
        db.session.refresh(row)
        return InstallationService.serialize(row)

    @staticmethod
    def update_status(installation_id: str, *, status: str, notes=None, technician_name=None):
        ctx = InstallationService._require(write=True)
        row = InstallationOrderRepository.get_by_id(ctx.tenant_id, installation_id)
        if row is None:
            raise NotFoundError("Installation job not found")
        new_status = (status or "").upper()
        if new_status not in ALLOWED_INSTALLATION_STATUSES:
            raise ValidationError("Invalid installation status")
        allowed = STATUS_TRANSITIONS.get(row.status, set())
        if new_status != row.status and new_status not in allowed:
            raise ValidationError(f"Cannot change status from {row.status} to {new_status}")
        old_status = row.status
        row.status = new_status
        if notes is not None:
            row.notes = (notes or "").strip() or None
        if technician_name is not None:
            row.technician_name = (technician_name or "").strip() or None
        if new_status == STATUS_COMPLETED:
            row.completed_at = utc_now_naive()
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_INSTALLATION_STATUS",
            entity_type="INSTALLATION_ORDER",
            entity_id=row.id,
            old_data={"status": old_status},
            new_data={"status": new_status},
        )
        if new_status == STATUS_COMPLETED and old_status != STATUS_COMPLETED:
            NotificationService.notify_installation_completed(
                tenant_id=ctx.tenant_id,
                installation_number=row.installation_number,
                serial=row.serial_unit.serial if row.serial_unit else "",
                user_id=ctx.user_id,
            )
        db.session.commit()
        db.session.refresh(row)
        return InstallationService.serialize(row)
