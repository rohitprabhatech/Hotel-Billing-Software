"""User request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER


class CreateUserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    role = fields.String(
        load_default=ROLE_BILLING_USER,
        validate=validate.OneOf([ROLE_BILLING_USER, ROLE_MANAGER]),
    )


class UpdateUserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    email = fields.Email(load_default=None)
    is_active = fields.Boolean(load_default=None)


class ResetPasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    password = fields.String(required=True, validate=validate.Length(min=8, max=128))


create_user_schema = CreateUserSchema()
update_user_schema = UpdateUserSchema()
reset_password_schema = ResetPasswordSchema()