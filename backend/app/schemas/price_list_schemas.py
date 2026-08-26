"""Wholesale price list request schemas (BIZ-51)."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema

from app.models.price_list import ALLOWED_LIST_TYPES


class PriceListItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    unit_price = fields.Decimal(required=True, as_string=False)
    is_active = fields.Boolean(load_default=True)


class CreatePriceListSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    list_type = fields.String(load_default="WHOLESALE", validate=validate.OneOf(sorted(ALLOWED_LIST_TYPES)))
    is_default = fields.Boolean(load_default=False)
    is_active = fields.Boolean(load_default=True)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class UpdatePriceListSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, validate=validate.Length(min=1, max=120))
    list_type = fields.String(load_default=None, validate=validate.OneOf(sorted(ALLOWED_LIST_TYPES)))
    is_default = fields.Boolean(load_default=None, allow_none=True)
    is_active = fields.Boolean(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class ReplacePriceListItemsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(fields.Nested(PriceListItemSchema), required=True)


class AssignCustomerPriceListSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    price_list_id = fields.String(required=True, validate=validate.Length(min=1, max=36))


create_price_list_schema = CreatePriceListSchema()
update_price_list_schema = UpdatePriceListSchema()
replace_price_list_items_schema = ReplacePriceListItemsSchema()
assign_customer_price_list_schema = AssignCustomerPriceListSchema()
