"""Wastage request schemas (BIZ-18)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateWastageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    reason = fields.String(load_default=None, allow_none=True)
    category = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=80))
    wastage_date = fields.Date(load_default=None, allow_none=True)


create_wastage_schema = CreateWastageSchema()
