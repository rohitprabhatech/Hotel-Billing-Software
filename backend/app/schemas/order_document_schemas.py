"""Sales / purchase order request schemas (BIZ-52)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.payments import ALLOWED_PAYMENT_METHODS, DEFAULT_PAYMENT_METHOD
from app.models.purchase_order import ALLOWED_PURCHASE_ORDER_STATUSES
from app.models.sales_order import ALLOWED_SALES_ORDER_STATUSES


class SalesOrderLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    unit_price = fields.Decimal(load_default=None, allow_none=True, as_string=False)


class CreateSalesOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(
        fields.Nested(SalesOrderLineSchema), required=True, validate=validate.Length(min=1)
    )
    customer_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )
    customer_name = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=120)
    )
    customer_phone = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=30)
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    discount = fields.Decimal(load_default=0, as_string=False)
    expected_delivery_date = fields.Date(load_default=None, allow_none=True)


class UpdateSalesOrderStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True, validate=validate.OneOf(sorted(ALLOWED_SALES_ORDER_STATUSES))
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class ConvertSalesOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    payment_method = fields.String(
        load_default=DEFAULT_PAYMENT_METHOD,
        validate=validate.OneOf(sorted(ALLOWED_PAYMENT_METHODS)),
    )


class PurchaseOrderLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    unit_cost = fields.Decimal(required=True, as_string=False)


class CreatePurchaseOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    items = fields.List(
        fields.Nested(PurchaseOrderLineSchema), required=True, validate=validate.Length(min=1)
    )
    supplier_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(min=1, max=36)
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    expected_date = fields.Date(load_default=None, allow_none=True)


class UpdatePurchaseOrderStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True, validate=validate.OneOf(sorted(ALLOWED_PURCHASE_ORDER_STATUSES))
    )
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class ConvertPurchaseOrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    payment_method = fields.String(
        load_default="cash",
        validate=validate.OneOf(["cash", "online", "credit"]),
    )
    invoice_number = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=60)
    )


create_sales_order_schema = CreateSalesOrderSchema()
update_sales_order_status_schema = UpdateSalesOrderStatusSchema()
convert_sales_order_schema = ConvertSalesOrderSchema()
create_purchase_order_schema = CreatePurchaseOrderSchema()
update_purchase_order_status_schema = UpdatePurchaseOrderStatusSchema()
convert_purchase_order_schema = ConvertPurchaseOrderSchema()
