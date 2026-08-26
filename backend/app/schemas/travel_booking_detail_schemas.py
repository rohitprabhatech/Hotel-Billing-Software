"""Schemas for travel itinerary and document metadata (BIZ-58)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.models.travel_booking_detail import ALLOWED_DOCUMENT_TYPES, ALLOWED_ITINERARY_TYPES


class CreateItineraryItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_type = fields.String(
        load_default="ACTIVITY",
        validate=validate.OneOf(sorted(ALLOWED_ITINERARY_TYPES)),
    )
    day_number = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=3650))
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=4000))
    location = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))
    vendor_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=160))
    confirmation_ref = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    start_at = fields.String(load_default=None, allow_none=True)
    end_at = fields.String(load_default=None, allow_none=True)
    sort_order = fields.Integer(load_default=0, validate=validate.Range(min=0, max=10000))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class UpdateItineraryItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_type = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(sorted(ALLOWED_ITINERARY_TYPES)),
    )
    day_number = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=1, max=3650))
    title = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=4000))
    location = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))
    vendor_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=160))
    confirmation_ref = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    start_at = fields.String(load_default=None, allow_none=True)
    end_at = fields.String(load_default=None, allow_none=True)
    sort_order = fields.Integer(load_default=None, allow_none=True, validate=validate.Range(min=0, max=10000))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class CreateBookingDocumentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    document_type = fields.String(
        load_default="OTHER",
        validate=validate.OneOf(sorted(ALLOWED_DOCUMENT_TYPES)),
    )
    holder_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    document_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    issued_country = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    expiry_date = fields.String(load_default=None, allow_none=True)
    file_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


create_itinerary_item_schema = CreateItineraryItemSchema()
update_itinerary_item_schema = UpdateItineraryItemSchema()
create_booking_document_schema = CreateBookingDocumentSchema()
