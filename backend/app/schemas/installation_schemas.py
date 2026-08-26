"""Installation order request schemas (BIZ-33 / BIZ-49)."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema

from app.models.installation_order import ALLOWED_INSTALLATION_STATUSES


class CreateInstallationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    serial_unit_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    custom_order_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    scheduled_at = fields.String(required=True, validate=validate.Length(min=1, max=40))
    install_address = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    bill_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    technician_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    estimated_charge = fields.Decimal(load_default=None, allow_none=True, as_string=False)

    @validates_schema
    def validate_source(self, data, **_kwargs):
        serial = (data.get("serial_unit_id") or "").strip()
        order = (data.get("custom_order_id") or "").strip()
        if serial and order:
            raise ValidationError("Provide serial_unit_id or custom_order_id, not both")
        if not serial and not order:
            raise ValidationError("serial_unit_id or custom_order_id is required")


class UpdateInstallationStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(required=True, validate=validate.OneOf(sorted(ALLOWED_INSTALLATION_STATUSES)))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    technician_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))


create_installation_schema = CreateInstallationSchema()
update_installation_status_schema = UpdateInstallationStatusSchema()
