"""Auth request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate, validates_schema, ValidationError


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class RegisterHotelSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    hotel_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    business_name = fields.String(load_default=None, validate=validate.Length(max=200))
    address = fields.String(load_default=None, validate=validate.Length(max=255))
    city = fields.String(load_default=None, validate=validate.Length(max=100))
    state = fields.String(load_default=None, validate=validate.Length(max=100))
    pincode = fields.String(load_default=None, validate=validate.Length(max=20))
    mobile = fields.String(load_default=None, validate=validate.Length(max=30))
    phone = fields.String(load_default=None, validate=validate.Length(max=30))
    email = fields.Email(load_default=None)
    gst_number = fields.String(load_default=None, validate=validate.Length(max=30))
    fssai_number = fields.String(load_default=None, validate=validate.Length(max=50))
    owner_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    owner_email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.String(required=True, validate=validate.Length(min=8, max=128))

    @validates_schema
    def passwords_match(self, data, **kwargs):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError("Password and confirm password do not match", "confirm_password")


class TokenSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    token = fields.String(required=True, validate=validate.Length(min=10))


class EmailOnlySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    token = fields.String(required=True, validate=validate.Length(min=10))
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.String(required=True, validate=validate.Length(min=8, max=128))

    @validates_schema
    def passwords_match(self, data, **kwargs):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError("Password and confirm password do not match", "confirm_password")


class ChangePasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    current_password = fields.String(required=True, validate=validate.Length(min=1))
    new_password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.String(required=True, validate=validate.Length(min=8, max=128))

    @validates_schema
    def passwords_match(self, data, **kwargs):
        if data.get("new_password") != data.get("confirm_password"):
            raise ValidationError("Password and confirm password do not match", "confirm_password")


login_schema = LoginSchema()
register_hotel_schema = RegisterHotelSchema()
token_schema = TokenSchema()
email_only_schema = EmailOnlySchema()
reset_password_schema = ResetPasswordSchema()
change_password_schema = ChangePasswordSchema()
