"""Batch / expiry schemas (BIZ-22)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateBatchSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    expiry_date = fields.Date(required=True)
    batch_code = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    reason = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=500))


class AdjustBatchSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    delta = fields.Decimal(required=True, as_string=False)
    reason = fields.String(required=True, validate=validate.Length(min=1, max=500))


create_batch_schema = CreateBatchSchema()
adjust_batch_schema = AdjustBatchSchema()
