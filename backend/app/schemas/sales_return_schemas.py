"""Sales return / exchange request schemas (BIZ-27)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.models.sales_return import ALLOWED_RETURN_KINDS


class ReturnLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    bill_item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    exchange_item_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=36)
    )
    exchange_variant_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=36)
    )


class CreateSalesReturnSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    bill_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    kind = fields.String(
        load_default="RETURN",
        validate=validate.OneOf(sorted(ALLOWED_RETURN_KINDS)),
    )
    reason = fields.String(required=True, validate=validate.Length(min=1, max=1000))
    items = fields.List(fields.Nested(ReturnLineSchema), required=True, validate=validate.Length(min=1))


create_sales_return_schema = CreateSalesReturnSchema()
