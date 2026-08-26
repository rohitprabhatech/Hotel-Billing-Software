"""Repair order request schemas (BIZ-31)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.models.repair_order import ALLOWED_REPAIR_STATUSES


class CreateRepairSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    serial_unit_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    issue_description = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    bill_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    estimated_charge = fields.Decimal(load_default=None, allow_none=True, as_string=False)


class UpdateRepairStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(required=True, validate=validate.OneOf(sorted(ALLOWED_REPAIR_STATUSES)))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


create_repair_schema = CreateRepairSchema()
update_repair_status_schema = UpdateRepairStatusSchema()
