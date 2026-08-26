"""Delivery job request schemas (BIZ-49)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.models.delivery_job import ALLOWED_DELIVERY_STATUSES


class CreateDeliverySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    custom_order_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    delivery_address = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    scheduled_at = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=40))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    driver_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    vehicle_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=40))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class UpdateDeliveryStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(required=True, validate=validate.OneOf(sorted(ALLOWED_DELIVERY_STATUSES)))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    driver_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    vehicle_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=40))


create_delivery_schema = CreateDeliverySchema()
update_delivery_status_schema = UpdateDeliveryStatusSchema()
