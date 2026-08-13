"""Tenant request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class UpdateTenantSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    business_name = fields.String(load_default=None, validate=validate.Length(min=1, max=200))
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


update_tenant_schema = UpdateTenantSchema()