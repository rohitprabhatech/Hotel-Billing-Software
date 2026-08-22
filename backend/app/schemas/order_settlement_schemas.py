"""Order settlement request schemas (BIZ-15)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import ALLOWED_PAYMENT_METHODS, DEFAULT_PAYMENT_METHOD


class OrderSettleSplitSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    order_item_ids = fields.List(
        fields.String(validate=validate.Length(min=1, max=36)),
        required=True,
        validate=validate.Length(min=1),
    )
    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )
    customer_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone_country_code = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=8))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    customer_email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))


class SettleOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    discount = fields.Decimal(load_default=0, as_string=False)
    service_charge = fields.Decimal(load_default=0, as_string=False)
    service_charge_percent = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )
    customer_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone_country_code = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=8))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    customer_email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    splits = fields.List(fields.Nested(OrderSettleSplitSchema), load_default=None, allow_none=True)


class SplitOrderBillsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    order_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    discount = fields.Decimal(load_default=0, as_string=False)
    service_charge = fields.Decimal(load_default=0, as_string=False)
    service_charge_percent = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    splits = fields.List(
        fields.Nested(OrderSettleSplitSchema),
        required=True,
        validate=validate.Length(min=2),
    )


settle_order_schema = SettleOrderSchema()
split_order_bills_schema = SplitOrderBillsSchema()
