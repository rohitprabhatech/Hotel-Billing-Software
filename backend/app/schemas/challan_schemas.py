"""Delivery challan request schemas (BIZ-36)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import ALLOWED_PAYMENT_METHODS, DEFAULT_PAYMENT_METHOD
from app.models.delivery_challan import ALLOWED_CHALLAN_STATUSES


class ChallanLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    unit_price = fields.Decimal(load_default=None, allow_none=True, as_string=False)


class CreateChallanSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(
        fields.Nested(ChallanLineSchema), required=True, validate=validate.Length(min=1)
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
    delivery_address = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=2000)
    )
    vehicle_number = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=40)
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    quotation_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )
    transport_charge = fields.Decimal(load_default=0, as_string=False)


class UpdateChallanStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True, validate=validate.OneOf(sorted(ALLOWED_CHALLAN_STATUSES))
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class ConvertChallanSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )


create_challan_schema = CreateChallanSchema()
update_challan_status_schema = UpdateChallanStatusSchema()
convert_challan_schema = ConvertChallanSchema()
