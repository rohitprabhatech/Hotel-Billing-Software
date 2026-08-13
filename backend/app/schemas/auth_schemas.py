"""Auth request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


login_schema = LoginSchema()