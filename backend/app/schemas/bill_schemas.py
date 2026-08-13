"""Bill request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import ALLOWED_PAYMENT_METHODS, DEFAULT_PAYMENT_METHOD


class BillLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)


class CreateBillSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(
        fields.Nested(BillLineSchema), required=True, validate=validate.Length(min=1)
    )
    discount = fields.Decimal(load_default=0, as_string=False)
    table_number = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=30)
    )
    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )


class CancelBillSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reason = fields.String(required=True, validate=validate.Length(min=1, max=1000))


create_bill_schema = CreateBillSchema()
cancel_bill_schema = CancelBillSchema()