"""Order request schemas (BIZ-13)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.orders import ALLOWED_ORDER_CHANNELS


class OrderLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    addon_ids = fields.List(fields.String(), load_default=list)


class OrderComboSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    combo_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)


class CreateOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    channel = fields.String(required=True, validate=validate.OneOf(sorted(ALLOWED_ORDER_CHANNELS)))
    dining_table_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    customer_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone_country_code = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=8))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    delivery_address = fields.String(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True)
    items = fields.List(fields.Nested(OrderLineSchema), load_default=list)
    combos = fields.List(fields.Nested(OrderComboSchema), load_default=list)


class UpdateOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    customer_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    customer_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    customer_phone_country_code = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=8))
    customer_phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    delivery_address = fields.String(load_default=None, allow_none=True)
    notes = fields.String(load_default=None, allow_none=True)


class AddOrderItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    addon_ids = fields.List(fields.String(), load_default=list)


class UpdateOrderItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    quantity = fields.Decimal(required=True, as_string=False)


class CancelOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reason = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))


create_order_schema = CreateOrderSchema()
update_order_schema = UpdateOrderSchema()
add_order_item_schema = AddOrderItemSchema()
update_order_item_schema = UpdateOrderItemSchema()
cancel_order_schema = CancelOrderSchema()
