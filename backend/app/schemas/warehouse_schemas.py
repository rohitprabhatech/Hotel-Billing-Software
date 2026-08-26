"""Warehouse / stock-transfer request schemas (BIZ-38)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateWarehouseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    code = fields.String(required=True, validate=validate.Length(min=1, max=30))
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    address = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    is_default = fields.Boolean(load_default=False)


class UpdateWarehouseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(load_default=None, allow_none=True, validate=validate.Length(min=1, max=120))
    address = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    is_active = fields.Boolean(load_default=None, allow_none=True)
    is_default = fields.Boolean(load_default=None, allow_none=True)


class TransferLineSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)


class CreateStockTransferSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    from_warehouse_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    to_warehouse_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    items = fields.List(
        fields.Nested(TransferLineSchema), required=True, validate=validate.Length(min=1)
    )


create_warehouse_schema = CreateWarehouseSchema()
update_warehouse_schema = UpdateWarehouseSchema()
create_stock_transfer_schema = CreateStockTransferSchema()
