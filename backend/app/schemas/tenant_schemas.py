"""Tenant request schemas."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates

from app.constants.business_types import normalize_business_type


class UpdateTenantSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    business_name = fields.String(load_default=None, validate=validate.Length(min=1, max=200))
    business_type = fields.String(load_default=None, validate=validate.Length(min=1, max=40))
    address = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    city = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    state = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=100))
    pincode = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    email = fields.Email(load_default=None, allow_none=True)
    gst_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=30))
    fssai_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=50))
    bill_number_prefix = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=20)
    )
    default_gst_percent = fields.Decimal(load_default=None, allow_none=True, as_string=False)

    @validates("business_type")
    def validate_business_type(self, value, **kwargs):
        if value is None:
            return
        try:
            normalize_business_type(value, allow_legacy=False)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc


update_tenant_schema = UpdateTenantSchema()
