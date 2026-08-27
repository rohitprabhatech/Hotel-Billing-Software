"""Cafe coupon business logic (Sprint 5)."""

from datetime import date
from decimal import Decimal

from app.constants.permissions import PERM_ADDONS_READ, PERM_ADDONS_WRITE, PERM_BILLING
from app.extensions import db
from app.models.coupon import (
    ALLOWED_DISCOUNT_TYPES,
    DISCOUNT_AMOUNT,
    DISCOUNT_PERCENT,
    Coupon,
    CouponRedemption,
)
from app.repositories.coupon_repository import CouponRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive


class CouponService:
    @staticmethod
    def _require_cafe_coupons_module():
        ctx = require_request_context()
        from app.repositories.tenant_repository import TenantRepository

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None or not ModuleService.is_enabled_for_tenant(tenant, "addons_combos"):
            raise ValidationError("Coupons are only available for Cafe / Tea Shop")

    @staticmethod
    def list_coupons(*, active_only=False):
        require_permission(PERM_ADDONS_READ)
        CouponService._require_cafe_coupons_module()
        ctx = require_request_context()
        rows = CouponRepository.list_by_tenant(ctx.tenant_id, active_only=active_only)
        return [CouponService.serialize(row) for row in rows]

    @staticmethod
    def get_coupon(coupon_id: str):
        require_permission(PERM_ADDONS_READ)
        CouponService._require_cafe_coupons_module()
        ctx = require_request_context()
        row = CouponRepository.get_by_id(ctx.tenant_id, coupon_id)
        if row is None:
            raise NotFoundError("Coupon not found")
        return CouponService.serialize(row)

    @staticmethod
    def create_coupon(
        *,
        code: str,
        name: str,
        discount_type: str,
        discount_value,
        description=None,
        min_order_amount=None,
        max_discount_amount=None,
        starts_on=None,
        ends_on=None,
        usage_limit=None,
        is_active=True,
    ):
        require_permission(PERM_ADDONS_WRITE)
        CouponService._require_cafe_coupons_module()
        ctx = require_request_context()
        parsed = CouponService._parse_fields(
            code=code,
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            description=description,
            min_order_amount=min_order_amount,
            max_discount_amount=max_discount_amount,
            starts_on=starts_on,
            ends_on=ends_on,
            usage_limit=usage_limit,
        )
        existing = CouponRepository.get_by_code(ctx.tenant_id, parsed["code"])
        if existing:
            raise ConflictError("A coupon with this code already exists")

        coupon = Coupon(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            usage_count=0,
            is_active=bool(is_active),
            **parsed,
        )
        CouponRepository.add(coupon)
        serialized = CouponService.serialize(coupon)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_COUPON",
            entity_type="COUPON",
            entity_id=coupon.id,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def update_coupon(coupon_id: str, **fields):
        require_permission(PERM_ADDONS_WRITE)
        CouponService._require_cafe_coupons_module()
        ctx = require_request_context()
        coupon = CouponRepository.get_by_id(ctx.tenant_id, coupon_id)
        if coupon is None:
            raise NotFoundError("Coupon not found")
        old = CouponService.serialize(coupon)

        code = fields.get("code", coupon.code)
        name = fields.get("name", coupon.name)
        discount_type = fields.get("discount_type", coupon.discount_type)
        discount_value = fields.get("discount_value", coupon.discount_value)
        parsed = CouponService._parse_fields(
            code=code,
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            description=fields.get("description", coupon.description),
            min_order_amount=fields.get("min_order_amount", coupon.min_order_amount),
            max_discount_amount=fields.get("max_discount_amount", coupon.max_discount_amount),
            starts_on=fields.get("starts_on", coupon.starts_on),
            ends_on=fields.get("ends_on", coupon.ends_on),
            usage_limit=fields.get("usage_limit", coupon.usage_limit),
        )
        if parsed["code"] != coupon.code:
            clash = CouponRepository.get_by_code(ctx.tenant_id, parsed["code"])
            if clash and clash.id != coupon.id:
                raise ConflictError("A coupon with this code already exists")

        for key, value in parsed.items():
            setattr(coupon, key, value)
        if "is_active" in fields and fields["is_active"] is not None:
            coupon.is_active = bool(fields["is_active"])

        serialized = CouponService.serialize(coupon)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_COUPON",
            entity_type="COUPON",
            entity_id=coupon.id,
            old_data=old,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def deactivate_coupon(coupon_id: str):
        require_permission(PERM_ADDONS_WRITE)
        CouponService._require_cafe_coupons_module()
        ctx = require_request_context()
        coupon = CouponRepository.get_by_id(ctx.tenant_id, coupon_id)
        if coupon is None:
            raise NotFoundError("Coupon not found")
        old = CouponService.serialize(coupon)
        coupon.is_active = False
        serialized = CouponService.serialize(coupon)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DEACTIVATE_COUPON",
            entity_type="COUPON",
            entity_id=coupon.id,
            old_data=old,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def preview(*, code: str, subtotal):
        """Validate coupon for POS without redeeming."""
        require_permission(PERM_BILLING)
        CouponService._require_cafe_coupons_module()
        ctx = require_request_context()
        coupon, discount_amount = CouponService._resolve_for_subtotal(
            ctx.tenant_id, code=code, subtotal=subtotal
        )
        return {
            "coupon": CouponService.serialize(coupon),
            "discount_amount": float(discount_amount),
            "subtotal": float(money(subtotal or 0)),
        }

    @staticmethod
    def resolve_for_settle(*, code: str | None, subtotal):
        """Used inside settle transaction — no commit."""
        if not code or not str(code).strip():
            return None, money(0)
        ctx = require_request_context()
        from app.repositories.tenant_repository import TenantRepository

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None or not ModuleService.is_enabled_for_tenant(tenant, "addons_combos"):
            raise ValidationError("Coupons are only available for Cafe / Tea Shop")
        return CouponService._resolve_for_subtotal(ctx.tenant_id, code=code, subtotal=subtotal)

    @staticmethod
    def redeem(*, coupon: Coupon, bill_id: str, order_id: str | None, discount_applied, user_id: str):
        """Increment usage + write redemption row (same DB transaction as settle)."""
        coupon.usage_count = int(coupon.usage_count or 0) + 1
        CouponRepository.add_redemption(
            CouponRedemption(
                id=new_uuid(),
                tenant_id=coupon.tenant_id,
                coupon_id=coupon.id,
                bill_id=bill_id,
                order_id=order_id,
                discount_applied=money(discount_applied),
                redeemed_by=user_id,
            )
        )

    @staticmethod
    def _resolve_for_subtotal(tenant_id: str, *, code: str, subtotal):
        normalized = (code or "").strip().upper()
        if not normalized:
            raise ValidationError("Coupon code is required")
        coupon = CouponRepository.get_by_code(tenant_id, normalized)
        if coupon is None or not coupon.is_active:
            raise ValidationError("Invalid or inactive coupon code")

        today = utc_now_naive().date()
        if coupon.starts_on and today < coupon.starts_on:
            raise ValidationError("This coupon is not active yet")
        if coupon.ends_on and today > coupon.ends_on:
            raise ValidationError("This coupon has expired")
        if coupon.usage_limit is not None and int(coupon.usage_count or 0) >= int(coupon.usage_limit):
            raise ValidationError("This coupon has reached its usage limit")

        order_subtotal = money(subtotal or 0)
        if order_subtotal <= 0:
            raise ValidationError("Cart subtotal must be greater than zero to use a coupon")
        if coupon.min_order_amount is not None and order_subtotal < money(coupon.min_order_amount):
            raise ValidationError(
                f"Minimum order amount for this coupon is ₹{float(coupon.min_order_amount):.2f}"
            )

        if coupon.discount_type == DISCOUNT_PERCENT:
            raw = money(order_subtotal * (Decimal(coupon.discount_value) / Decimal("100")))
            if coupon.max_discount_amount is not None:
                raw = min(raw, money(coupon.max_discount_amount))
        else:
            raw = money(coupon.discount_value)

        discount_amount = min(raw, order_subtotal)
        if discount_amount <= 0:
            raise ValidationError("Coupon discount must be greater than zero")
        return coupon, discount_amount

    @staticmethod
    def _parse_fields(
        *,
        code,
        name,
        discount_type,
        discount_value,
        description=None,
        min_order_amount=None,
        max_discount_amount=None,
        starts_on=None,
        ends_on=None,
        usage_limit=None,
    ):
        parsed_code = (code or "").strip().upper()
        if not parsed_code:
            raise ValidationError("Coupon code is required")
        if len(parsed_code) > 40:
            raise ValidationError("Coupon code is too long")
        parsed_name = (name or "").strip()
        if not parsed_name:
            raise ValidationError("Coupon name is required")

        dtype = (discount_type or DISCOUNT_AMOUNT).strip().lower()
        if dtype not in ALLOWED_DISCOUNT_TYPES:
            raise ValidationError("discount_type must be percent or amount")

        value = money(discount_value)
        if value <= 0:
            raise ValidationError("discount_value must be greater than zero")
        if dtype == DISCOUNT_PERCENT and value > money(100):
            raise ValidationError("Percent discount cannot exceed 100")

        min_amount = None if min_order_amount in (None, "") else money(min_order_amount)
        max_amount = None if max_discount_amount in (None, "") else money(max_discount_amount)
        if max_amount is not None and max_amount <= 0:
            raise ValidationError("max_discount_amount must be greater than zero")

        start = CouponService._parse_date(starts_on)
        end = CouponService._parse_date(ends_on)
        if start and end and end < start:
            raise ValidationError("ends_on must be on or after starts_on")

        limit = None
        if usage_limit not in (None, ""):
            try:
                limit = int(usage_limit)
            except (TypeError, ValueError) as exc:
                raise ValidationError("usage_limit must be an integer") from exc
            if limit < 1:
                raise ValidationError("usage_limit must be at least 1")

        return {
            "code": parsed_code,
            "name": parsed_name,
            "description": (description or "").strip() or None,
            "discount_type": dtype,
            "discount_value": value,
            "min_order_amount": min_amount,
            "max_discount_amount": max_amount,
            "starts_on": start,
            "ends_on": end,
            "usage_limit": limit,
        }

    @staticmethod
    def _parse_date(value) -> date | None:
        if value in (None, ""):
            return None
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError as exc:
            raise ValidationError("Invalid date format (use YYYY-MM-DD)") from exc

    @staticmethod
    def serialize(coupon: Coupon):
        return {
            "id": coupon.id,
            "code": coupon.code,
            "name": coupon.name,
            "description": coupon.description,
            "discount_type": coupon.discount_type,
            "discount_value": float(coupon.discount_value),
            "min_order_amount": float(coupon.min_order_amount)
            if coupon.min_order_amount is not None
            else None,
            "max_discount_amount": float(coupon.max_discount_amount)
            if coupon.max_discount_amount is not None
            else None,
            "starts_on": coupon.starts_on.isoformat() if coupon.starts_on else None,
            "ends_on": coupon.ends_on.isoformat() if coupon.ends_on else None,
            "usage_limit": coupon.usage_limit,
            "usage_count": int(coupon.usage_count or 0),
            "is_active": bool(coupon.is_active),
            "created_at": coupon.created_at.isoformat() if coupon.created_at else None,
            "updated_at": coupon.updated_at.isoformat() if coupon.updated_at else None,
        }
