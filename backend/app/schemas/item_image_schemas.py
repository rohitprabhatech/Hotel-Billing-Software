"""Item image request schemas (BIZ-26)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateItemImageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    image_url = fields.String(required=True, validate=validate.Length(min=8, max=500))
    variant_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    alt_text = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    is_primary = fields.Boolean(load_default=False)


create_item_image_schema = CreateItemImageSchema()
