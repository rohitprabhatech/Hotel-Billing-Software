"""Customer request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateCustomerSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    phone_country_code = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=8)
    )
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    credit_limit = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    notes = fields.String(load_default=None, allow_none=True)


class UpdateCustomerSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    phone_country_code = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=8)
    )
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    email = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
    credit_limit = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    notes = fields.String(load_default=None, allow_none=True)


class StatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_active = fields.Boolean(required=True)


create_customer_schema = CreateCustomerSchema()
update_customer_schema = UpdateCustomerSchema()
status_schema = StatusSchema()
