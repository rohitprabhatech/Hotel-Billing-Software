"""Cafe add-on and combo request schemas (BIZ-17)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class AddonOptionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    extra_price = fields.Decimal(load_default=0, as_string=False)
    linked_item_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    is_default = fields.Boolean(load_default=False)


class CreateAddonGroupSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    menu_item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    is_required = fields.Boolean(load_default=False)
    max_selections = fields.Integer(load_default=None, allow_none=True)
    addons = fields.List(fields.Nested(AddonOptionSchema), load_default=list)


class ComboLineItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(load_default=1, as_string=False)


class CreateComboSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default=None, allow_none=True)
    combo_price = fields.Decimal(required=True, as_string=False)
    is_popular = fields.Boolean(load_default=False)
    items = fields.List(fields.Nested(ComboLineItemSchema), required=True, validate=validate.Length(min=1))


create_addon_group_schema = CreateAddonGroupSchema()
create_combo_schema = CreateComboSchema()
