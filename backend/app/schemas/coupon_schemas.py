"""Coupon request schemas (Sprint 5)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.models.coupon import ALLOWED_DISCOUNT_TYPES


class CreateCouponSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(required=True, validate=validate.Length(min=1, max=40))
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default=None, allow_none=True)
    discount_type = fields.String(
        required=True, validate=validate.OneOf(sorted(ALLOWED_DISCOUNT_TYPES))
    )
    discount_value = fields.Decimal(required=True, as_string=False)
    min_order_amount = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    max_discount_amount = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    starts_on = fields.Date(load_default=None, allow_none=True)
    ends_on = fields.Date(load_default=None, allow_none=True)
    usage_limit = fields.Integer(load_default=None, allow_none=True)
    is_active = fields.Boolean(load_default=True)


class UpdateCouponSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=40))
    name = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=120))
    description = fields.String(load_default=None, allow_none=True)
    discount_type = fields.String(
        load_default=None, allow_none=True, validate=validate.OneOf(sorted(ALLOWED_DISCOUNT_TYPES))
    )
    discount_value = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    min_order_amount = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    max_discount_amount = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    starts_on = fields.Date(load_default=None, allow_none=True)
    ends_on = fields.Date(load_default=None, allow_none=True)
    usage_limit = fields.Integer(load_default=None, allow_none=True)
    is_active = fields.Boolean(load_default=None, allow_none=True)


class PreviewCouponSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(required=True, validate=validate.Length(min=1, max=40))
    subtotal = fields.Decimal(required=True, as_string=False)


create_coupon_schema = CreateCouponSchema()
update_coupon_schema = UpdateCouponSchema()
preview_coupon_schema = PreviewCouponSchema()
