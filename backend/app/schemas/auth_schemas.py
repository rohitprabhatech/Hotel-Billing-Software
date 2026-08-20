"""Auth request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate, validates_schema, ValidationError

from app.constants.business_types import ALLOWED_BUSINESS_TYPES


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class RegisterBusinessSchema(Schema):
    """Public business registration payload.

    Accepts legacy ``hotel_name`` as an alias for display name.
    """

    class Meta:
        unknown = EXCLUDE

    business_name = fields.String(load_default=None, validate=validate.Length(max=200))
    business_type = fields.String(required=True, validate=validate.Length(min=1, max=40))
    name = fields.String(load_default=None, validate=validate.Length(max=120))
    hotel_name = fields.String(load_default=None, validate=validate.Length(max=120))  # legacy
    address = fields.String(load_default=None, validate=validate.Length(max=255))
    city = fields.String(load_default=None, validate=validate.Length(max=100))
    state = fields.String(load_default=None, validate=validate.Length(max=100))
    pincode = fields.String(load_default=None, validate=validate.Length(max=20))
    country = fields.String(load_default="India", validate=validate.Length(max=80))
    mobile = fields.String(load_default=None, validate=validate.Length(max=30))
    phone = fields.String(load_default=None, validate=validate.Length(max=30))
    email = fields.Email(load_default=None)
    gst_number = fields.String(load_default=None, validate=validate.Length(max=30))
    fssai_number = fields.String(load_default=None, validate=validate.Length(max=50))
    owner_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    owner_email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    terms_accepted = fields.Boolean(required=True)

    @validates_schema
    def validate_register(self, data, **kwargs):
        if not data.get("terms_accepted"):
            raise ValidationError(
                "You must agree to the Terms of Service and Privacy Policy",
                "terms_accepted",
            )
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError(
                "Password and confirm password do not match", "confirm_password"
            )
        business_name = (data.get("business_name") or "").strip()
        display_name = (data.get("name") or data.get("hotel_name") or "").strip()
        if not business_name and not display_name:
            raise ValidationError("Business name is required", "business_name")
        if not business_name:
            data["business_name"] = display_name
        if not display_name:
            data["name"] = data["business_name"]
        business_type = (data.get("business_type") or "").strip().lower()
        if not business_type:
            raise ValidationError("Business type is required", "business_type")
        if business_type not in ALLOWED_BUSINESS_TYPES:
            raise ValidationError("Invalid business type", "business_type")
        data["business_type"] = business_type


# Backward-compatible alias
RegisterHotelSchema = RegisterBusinessSchema


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
register_business_schema = RegisterBusinessSchema()
register_hotel_schema = register_business_schema  # legacy alias
token_schema = TokenSchema()
email_only_schema = EmailOnlySchema()
reset_password_schema = ResetPasswordSchema()
change_password_schema = ChangePasswordSchema()
