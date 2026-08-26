"""Furniture delivery job workflows (BIZ-49)."""

from datetime import datetime

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.custom_order import (
    ORDER_TYPE_FURNITURE,
    STATUS_DELIVERED as ORDER_STATUS_DELIVERED,
    STATUS_READY,
)
from app.models.delivery_job import (
    ALLOWED_DELIVERY_STATUSES,
    STATUS_DELIVERED,
    STATUS_OUT_FOR_DELIVERY,
    STATUS_SCHEDULED,
    STATUS_TRANSITIONS,
    DeliveryJob,
)
from app.models.role import ROLE_BILLING_USER
from app.repositories.custom_order_repository import CustomOrderRepository
from app.repositories.delivery_job_repository import DeliveryJobRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive

MODULE = "delivery_tracking"


class DeliveryService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage deliveries")
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
    def serialize(row: DeliveryJob) -> dict:
        order = row.custom_order
        return {
            "id": row.id,
            "delivery_number": row.delivery_number,
            "status": row.status,
            "custom_order_id": row.custom_order_id,
            "custom_order_number": order.order_number if order else None,
            "custom_order_title": order.title if order else None,
            "bill_id": row.bill_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "delivery_address": row.delivery_address,
            "scheduled_at": row.scheduled_at.isoformat() if row.scheduled_at else None,
            "driver_name": row.driver_name,
            "vehicle_number": row.vehicle_number,
            "notes": row.notes,
            "out_for_delivery_at": (
                row.out_for_delivery_at.isoformat() if row.out_for_delivery_at else None
            ),
            "delivered_at": row.delivered_at.isoformat() if row.delivered_at else None,
            "created_by": row.created_by,
            "created_by_name": row.creator.name if row.creator else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def list_jobs(
        *,
        status=None,
        custom_order_id=None,
        from_date=None,
        to_date=None,
        page=1,
        per_page=100,
    ):
        ctx = DeliveryService._require(write=False)
        start = DeliveryService._parse_scheduled_at(from_date) if from_date else None
        end = DeliveryService._parse_scheduled_at(to_date) if to_date else None
        rows, total = DeliveryJobRepository.list_for_tenant(
            ctx.tenant_id,
            status=status,
            custom_order_id=custom_order_id,
            from_date=start,
            to_date=end,
            page=page,
            per_page=per_page,
        )
        return (
            [DeliveryService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get_job(delivery_id: str):
        ctx = DeliveryService._require(write=False)
        row = DeliveryJobRepository.get_by_id(ctx.tenant_id, delivery_id)
        if row is None:
            raise NotFoundError("Delivery job not found")
        return DeliveryService.serialize(row)

    @staticmethod
    def create(
        *,
        custom_order_id: str,
        delivery_address: str,
        scheduled_at=None,
        customer_name=None,
        customer_phone=None,
        driver_name=None,
        vehicle_number=None,
        notes=None,
    ):
        ctx = DeliveryService._require(write=True)
        order = CustomOrderRepository.get_by_id(ctx.tenant_id, custom_order_id.strip())
        if order is None:
            raise NotFoundError("Custom order not found")
        if order.order_type != ORDER_TYPE_FURNITURE:
            raise ValidationError("Delivery jobs can only be created for furniture orders")
        if order.status != STATUS_READY:
            raise ValidationError("Custom order must be READY before scheduling delivery")
        if DeliveryJobRepository.find_active_for_custom_order(ctx.tenant_id, order.id):
            raise ValidationError("An active delivery job already exists for this order")

        address = (delivery_address or "").strip()
        if not address:
            raise ValidationError("Delivery address is required")

        schedule = DeliveryService._parse_scheduled_at(scheduled_at) or order.delivery_at
        sequence, delivery_number = DeliveryJobRepository.allocate_number(ctx.tenant_id)

        row = DeliveryJob(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            delivery_number=delivery_number,
            delivery_sequence=sequence,
            custom_order_id=order.id,
            customer_name=(customer_name or "").strip() or order.customer_name,
            customer_phone=(customer_phone or "").strip() or order.customer_phone,
            delivery_address=address,
            scheduled_at=schedule,
            status=STATUS_SCHEDULED,
            driver_name=(driver_name or "").strip() or None,
            vehicle_number=(vehicle_number or "").strip() or None,
            notes=(notes or "").strip() or None,
            created_by=ctx.user_id,
        )
        DeliveryJobRepository.add(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_DELIVERY_JOB",
            entity_type="DELIVERY_JOB",
            entity_id=row.id,
            new_data={
                "delivery_number": delivery_number,
                "custom_order_number": order.order_number,
                "status": STATUS_SCHEDULED,
            },
        )
        db.session.commit()
        db.session.refresh(row)
        return DeliveryService.serialize(row)

    @staticmethod
    def update_status(
        delivery_id: str,
        *,
        status: str,
        notes=None,
        driver_name=None,
        vehicle_number=None,
    ):
        ctx = DeliveryService._require(write=True)
        row = DeliveryJobRepository.get_by_id(ctx.tenant_id, delivery_id)
        if row is None:
            raise NotFoundError("Delivery job not found")
        new_status = (status or "").upper()
        if new_status not in ALLOWED_DELIVERY_STATUSES:
            raise ValidationError("Invalid delivery status")
        allowed = STATUS_TRANSITIONS.get(row.status, set())
        if new_status != row.status and new_status not in allowed:
            raise ValidationError(f"Cannot change status from {row.status} to {new_status}")

        old_status = row.status
        row.status = new_status
        if notes is not None:
            row.notes = (notes or "").strip() or None
        if driver_name is not None:
            row.driver_name = (driver_name or "").strip() or None
        if vehicle_number is not None:
            row.vehicle_number = (vehicle_number or "").strip() or None

        if new_status == STATUS_OUT_FOR_DELIVERY and old_status != STATUS_OUT_FOR_DELIVERY:
            row.out_for_delivery_at = utc_now_naive()
            NotificationService.notify_delivery_out_for_delivery(
                tenant_id=ctx.tenant_id,
                delivery_number=row.delivery_number,
                customer_name=row.customer_name or "Customer",
                user_id=ctx.user_id,
            )

        if new_status == STATUS_DELIVERED and old_status != STATUS_DELIVERED:
            row.delivered_at = utc_now_naive()
            if row.custom_order_id:
                order = CustomOrderRepository.get_by_id(ctx.tenant_id, row.custom_order_id)
                if order is not None and order.status == STATUS_READY:
                    order.status = ORDER_STATUS_DELIVERED
                    order.delivered_at = row.delivered_at
            NotificationService.notify_delivery_completed(
                tenant_id=ctx.tenant_id,
                delivery_number=row.delivery_number,
                customer_name=row.customer_name or "Customer",
                user_id=ctx.user_id,
            )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_DELIVERY_STATUS",
            entity_type="DELIVERY_JOB",
            entity_id=row.id,
            old_data={"status": old_status},
            new_data={"status": new_status},
        )
        db.session.commit()
        db.session.refresh(row)
        return DeliveryService.serialize(row)
