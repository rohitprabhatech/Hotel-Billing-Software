"""Profile request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class UpdateProfileSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    phone = fields.String(load_default=None, validate=validate.Length(max=30))


class RequestEmailChangeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    new_email = fields.Email(required=True)


update_profile_schema = UpdateProfileSchema()
request_email_change_schema = RequestEmailChangeSchema()
