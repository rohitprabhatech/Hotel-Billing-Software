"""Supplier request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateSupplierSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    phone_country_code = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=8)
    )
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    gstin = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=15))
    email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    address = fields.String(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True)


class UpdateSupplierSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    phone_country_code = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=8)
    )
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    gstin = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=15))
    email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    address = fields.String(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True)


class StatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_active = fields.Boolean(required=True)


create_supplier_schema = CreateSupplierSchema()
update_supplier_schema = UpdateSupplierSchema()
status_schema = StatusSchema()
