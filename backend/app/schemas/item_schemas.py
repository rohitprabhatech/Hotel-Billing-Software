"""Item request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    category_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    sku = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    barcode = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    uom = fields.String(load_default="pcs", validate=validate.Length(max=16))
    description = fields.String(load_default=None, allow_none=True)
    price = fields.Decimal(required=True, as_string=False)
    cost_price = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    gst_percentage = fields.Decimal(load_default=0, as_string=False)
    stock_quantity = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    minimum_stock_level = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    is_menu = fields.Boolean(load_default=False)
    is_veg = fields.Boolean(load_default=None, allow_none=True)
    tracks_batches = fields.Boolean(load_default=False)
    block_expired_batches = fields.Boolean(load_default=True)


class UpdateItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=200))
    category_id = fields.String(load_default=None, validate=validate.Length(min=1, max=36))
    sku = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    barcode = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    uom = fields.String(load_default="pcs", validate=validate.Length(max=16))
    description = fields.String(load_default=None, allow_none=True)
    price = fields.Decimal(load_default=None, as_string=False)
    cost_price = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    gst_percentage = fields.Decimal(load_default=None, as_string=False)
    stock_quantity = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    minimum_stock_level = fields.Decimal(load_default=None, allow_none=True, as_string=False)
    is_menu = fields.Boolean(load_default=None, allow_none=True)
    is_veg = fields.Boolean(load_default=None, allow_none=True)
    tracks_batches = fields.Boolean(load_default=None, allow_none=True)
    block_expired_batches = fields.Boolean(load_default=None, allow_none=True)


class ItemStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    is_active = fields.Boolean(required=True)
    reason = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))


class AdjustStockSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    delta = fields.Decimal(required=True, as_string=False)
    reason = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))


class ReceiveStockSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    quantity = fields.Decimal(required=True, as_string=False)
    reason = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))


create_item_schema = CreateItemSchema()
update_item_schema = UpdateItemSchema()
item_status_schema = ItemStatusSchema()
adjust_stock_schema = AdjustStockSchema()
receive_stock_schema = ReceiveStockSchema()
