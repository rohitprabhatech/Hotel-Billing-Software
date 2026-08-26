"""Quotation request schemas (BIZ-36)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import ALLOWED_PAYMENT_METHODS, DEFAULT_PAYMENT_METHOD
from app.models.quotation import ALLOWED_QUOTATION_STATUSES


class QuotationLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    unit_price = fields.Decimal(load_default=None, allow_none=True, as_string=False)


class CreateQuotationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(
        fields.Nested(QuotationLineSchema), required=True, validate=validate.Length(min=1)
    )
    customer_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )
    customer_name = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=120)
    )
    customer_phone = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=30)
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    discount = fields.Decimal(load_default=0, as_string=False)
    valid_until = fields.Date(load_default=None, allow_none=True)


class UpdateQuotationStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True, validate=validate.OneOf(sorted(ALLOWED_QUOTATION_STATUSES))
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class ConvertQuotationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )


create_quotation_schema = CreateQuotationSchema()
update_quotation_status_schema = UpdateQuotationStatusSchema()
convert_quotation_schema = ConvertQuotationSchema()
