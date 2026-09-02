"""Travel booking schemas (BIZ-57)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import ALLOWED_PAYMENT_METHODS, DEFAULT_PAYMENT_METHOD
from app.models.travel_booking import ALLOWED_TRAVEL_BOOKING_STATUSES


class CreateTravelBookingSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    package_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    customer_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=36))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    pax_count = fields.Integer(load_default=1, validate=validate.Range(min=1, max=500))
    total_amount = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    advance_amount = fields.Decimal(load_default=0, as_string=False)
    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )
    travel_start_at = fields.String(load_default=None, allow_none=True)
    travel_end_at = fields.String(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    agent_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=36))
    commission_percent = fields.Decimal(load_default=None, allow_none=True, as_string=False)


class UpdateTravelBookingSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    pax_count = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=500))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    travel_start_at = fields.String(load_default=None, allow_none=True)
    travel_end_at = fields.String(load_default=None, allow_none=True)
    agent_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=36))


class UpdateTravelBookingStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True,
        validate=validate.OneOf(sorted(ALLOWED_TRAVEL_BOOKING_STATUSES)),
    )


class RecordTravelBookingPaymentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    amount = fields.Decimal(required=True, as_string=False)
    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=1000))


create_travel_booking_schema = CreateTravelBookingSchema()
update_travel_booking_schema = UpdateTravelBookingSchema()
update_travel_booking_status_schema = UpdateTravelBookingStatusSchema()
record_travel_booking_payment_schema = RecordTravelBookingPaymentSchema()
