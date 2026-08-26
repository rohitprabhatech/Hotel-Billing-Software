"""Production run request schemas (BIZ-40)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class CreateProductionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    recipe_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    quantity = fields.Decimal(required=True, as_string=False)
    notes = fields.String(load_default=None, allow_none=True)
    run_date = fields.Date(load_default=None, allow_none=True)
    expiry_date = fields.Date(load_default=None, allow_none=True)
    batch_code = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=60))


create_production_schema = CreateProductionSchema()
