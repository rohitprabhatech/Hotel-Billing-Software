"""Variant request schemas (BIZ-25)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class ItemVariantSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    size = fields.String(required=True, validate=validate.Length(min=1, max=32))
    color = fields.String(required=True, validate=validate.Length(min=1, max=64))
    brand = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    sku = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    barcode = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    stock_quantity = fields.Decimal(load_default=0, as_string=False)
    is_active = fields.Boolean(load_default=True)


class ReplaceItemVariantsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    variants = fields.List(fields.Nested(ItemVariantSchema), required=True)


class UpdateItemVariantSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    size = fields.String(load_default=None, validate=validate.Length(min=1, max=32))
    color = fields.String(load_default=None, validate=validate.Length(min=1, max=64))
    brand = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    sku = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    barcode = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    stock_quantity = fields.Decimal(load_default=None, as_string=False)
    is_active = fields.Boolean(load_default=None, allow_none=True)


create_item_variant_schema = ItemVariantSchema()
replace_item_variants_schema = ReplaceItemVariantsSchema()
update_item_variant_schema = UpdateItemVariantSchema()
