"""Bill request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import ALLOWED_PAYMENT_METHODS, DEFAULT_PAYMENT_METHOD


class BillLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    variant_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )
    serial_unit_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )
    serial = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=4, max=64)
    )
    quantity = fields.Decimal(required=True, as_string=False)


class CreateBillSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(
        fields.Nested(BillLineSchema), required=True, validate=validate.Length(min=1)
    )
    discount = fields.Decimal(load_default=0, as_string=False)
    # Generic bill reference (table / counter / token / order note).
    reference = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=30)
    )
    table_number = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=30)
    )  # legacy alias for reference
    transport_charge = fields.Decimal(load_default=0, as_string=False)
    warehouse_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )
    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )
    customer_name = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=120)
    )
    customer_phone_country_code = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=8)
    )
    customer_phone = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=20)
    )
    customer_email = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=255)
    )
    customer_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )


class CancelBillSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reason = fields.String(required=True, validate=validate.Length(min=1, max=1000))


class SendEmailBillSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=255)
    )
    customer_name = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=120)
    )


create_bill_schema = CreateBillSchema()
cancel_bill_schema = CancelBillSchema()
send_email_bill_schema = SendEmailBillSchema()