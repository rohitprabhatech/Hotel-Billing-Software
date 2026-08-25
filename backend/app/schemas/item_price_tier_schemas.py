"""Bulk / quantity price tier schemas (BIZ-21)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class PriceTierSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    min_quantity = fields.Decimal(required=True, as_string=False)
    unit_price = fields.Decimal(required=True, as_string=False)
    is_active = fields.Boolean(load_default=True)


class ReplacePriceTiersSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    tiers = fields.List(fields.Nested(PriceTierSchema), required=True)


create_price_tier_schema = PriceTierSchema()
replace_price_tiers_schema = ReplacePriceTiersSchema()
