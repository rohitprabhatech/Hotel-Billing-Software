"""Item request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    category_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    description = fields.String(load_default=None, allow_none=True)
    price = fields.Decimal(required=True, as_string=False)
    gst_percentage = fields.Decimal(load_default=0, as_string=False)


class UpdateItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=200))
    category_id = fields.String(load_default=None, validate=validate.Length(min=1, max=36))
    description = fields.String(load_default=None, allow_none=True)
    price = fields.Decimal(load_default=None, as_string=False)
    gst_percentage = fields.Decimal(load_default=None, as_string=False)


class ItemStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_active = fields.Boolean(required=True)
    reason = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))


create_item_schema = CreateItemSchema()
update_item_schema = UpdateItemSchema()
item_status_schema = ItemStatusSchema()
