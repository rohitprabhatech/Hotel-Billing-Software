"""Item accessory request schemas (BIZ-30)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class ReplaceItemAccessoriesSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    accessory_item_ids = fields.List(
        fields.String(validate=validate.Length(min=1, max=36)),
        load_default=list,
    )


replace_item_accessories_schema = ReplaceItemAccessoriesSchema()
