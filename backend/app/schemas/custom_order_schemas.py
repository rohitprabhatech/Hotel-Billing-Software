"""Custom product order schemas (BIZ-42)."""

from marshmallow import EXCLUDE, Schema, fields, validate

_PAYMENT_METHODS = ("cash", "upi", "card", "credit", "other")
_ORDER_TYPES = ("bakery", "furniture")


class CreateCustomOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    order_type = fields.String(
        load_default="bakery", validate=validate.OneOf(_ORDER_TYPES)
    )
    customer_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    size = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    flavor = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    quantity = fields.Decimal(load_default=1, as_string=False)
    total_amount = fields.Decimal(required=True, as_string=False)
    advance_amount = fields.Decimal(load_default=0, as_string=False)
    payment_method = fields.String(
        load_default="cash", validate=validate.OneOf(_PAYMENT_METHODS)
    )
    delivery_at = fields.DateTime(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True)


class UpdateCustomOrderStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(required=True, validate=validate.Length(min=1, max=20))
    notes = fields.String(load_default=None, allow_none=True)


class RecordAdvanceSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    amount = fields.Decimal(required=True, as_string=False)
    payment_method = fields.String(
        load_default="cash", validate=validate.OneOf(_PAYMENT_METHODS)
    )
    notes = fields.String(load_default=None, allow_none=True)


create_custom_order_schema = CreateCustomOrderSchema()
update_custom_order_status_schema = UpdateCustomOrderStatusSchema()
record_advance_schema = RecordAdvanceSchema()
