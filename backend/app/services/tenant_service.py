"""Tenant profile operations."""

from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.request_context import require_request_context


class TenantService:
    @staticmethod
    def get_my_tenant(*, full: bool = True):
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        return TenantService.serialize(tenant, full=full)

    @staticmethod
    def update_my_tenant(payload: dict):
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")

        old = TenantService.serialize(tenant, full=True)
        fields = [
            "name",
            "business_name",
            "address",
            "city",
            "state",
            "pincode",
            "phone",
            "email",
            "gst_number",
            "fssai_number",
            "bill_number_prefix",
        ]
        for field in fields:
            if field in payload and payload[field] is not None:
                value = payload[field]
                if isinstance(value, str):
                    value = value.strip()
                setattr(tenant, field, value or None)

        if "default_gst_percent" in payload:
            raw = payload["default_gst_percent"]
            if raw is None or raw == "":
                tenant.default_gst_percent = None
            else:
                try:
                    gst = Decimal(str(raw))
                except (InvalidOperation, ValueError) as exc:
                    raise ValidationError("Invalid default GST percentage") from exc
                if gst < 0 or gst > 100:
                    raise ValidationError("GST percentage must be between 0 and 100")
                tenant.default_gst_percent = gst

        if not tenant.business_name:
            raise ValidationError("Business name is required")
        if not tenant.name:
            raise ValidationError("Hotel name is required")

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_TENANT",
            entity_type="TENANT",
            entity_id=tenant.id,
            old_data=old,
            new_data=TenantService.serialize(tenant, full=True),
        )
        db.session.commit()
        return TenantService.serialize(tenant, full=True)

    @staticmethod
    def serialize(tenant, *, full: bool = True):
        data = {
            "id": tenant.id,
            "name": tenant.name,
            "business_name": tenant.business_name,
            "status": tenant.status,
        }
        if full:
            data.update(
                {
                    "address": tenant.address,
                    "city": tenant.city,
                    "state": tenant.state,
                    "pincode": tenant.pincode,
                    "phone": tenant.phone,
                    "email": tenant.email,
                    "gst_number": tenant.gst_number,
                    "fssai_number": tenant.fssai_number,
                    "bill_number_prefix": tenant.bill_number_prefix,
                    "default_gst_percent": (
                        float(tenant.default_gst_percent)
                        if tenant.default_gst_percent is not None
                        else None
                    ),
                }
            )
        return data
