"""Tenant billing / invoice print settings."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema

ALLOWED_PAPER_SIZES = frozenset({"58mm", "80mm", "A4", "A5", "custom"})


class BillingSettingsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    paper_size = fields.String(required=True, validate=validate.OneOf(sorted(ALLOWED_PAPER_SIZES)))
    width_mm = fields.Integer(load_default=None, allow_none=True)
    height_mm = fields.Integer(load_default=None, allow_none=True)

    @validates_schema
    def validate_dimensions(self, data, **kwargs):
        paper = data.get("paper_size")
        width = data.get("width_mm")
        height = data.get("height_mm")

        if paper == "58mm":
            if width is not None and width != 58:
                raise ValidationError("Width must be 58 mm for 58mm preset", "width_mm")
            if height is not None and height <= 0:
                raise ValidationError("Height must be positive or omitted for auto", "height_mm")
            return

        if paper == "80mm":
            if width is not None and width != 80:
                raise ValidationError("Width must be 80 mm for 80mm preset", "width_mm")
            if height is not None and height <= 0:
                raise ValidationError("Height must be positive or omitted for auto", "height_mm")
            return

        if paper == "A4":
            if width is not None and width != 210:
                raise ValidationError("Width must be 210 mm for A4", "width_mm")
            if height is not None and height != 297:
                raise ValidationError("Height must be 297 mm for A4", "height_mm")
            return

        if paper == "A5":
            if width is not None and width != 148:
                raise ValidationError("Width must be 148 mm for A5", "width_mm")
            if height is not None and height != 210:
                raise ValidationError("Height must be 210 mm for A5", "height_mm")
            return

        if paper == "custom":
            if width is None or width < 40 or width > 300:
                raise ValidationError("Custom width must be between 40 and 300 mm", "width_mm")
            if height is not None and (height < 50 or height > 500):
                raise ValidationError("Custom height must be between 50 and 500 mm", "height_mm")


billing_settings_schema = BillingSettingsSchema()
