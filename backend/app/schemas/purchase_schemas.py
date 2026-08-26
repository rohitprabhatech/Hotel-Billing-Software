"""Purchase request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class PurchaseLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    unit_cost = fields.Decimal(required=True, as_string=False)


class CreatePurchaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    supplier_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=36))
    invoice_number = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=60))
    notes = fields.String(load_default=None, allow_none=True)
    payment_method = fields.String(
        load_default="cash",
        validate=validate.OneOf(["cash", "online", "credit"]),
    )
    items = fields.List(
        fields.Nested(PurchaseLineSchema), required=True, validate=validate.Length(min=1)
    )


class CancelPurchaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reason = fields.String(required=True, validate=validate.Length(min=1, max=1000))


create_purchase_schema = CreatePurchaseSchema()
cancel_purchase_schema = CancelPurchaseSchema()
