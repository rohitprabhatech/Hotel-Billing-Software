"""KOT request schemas (BIZ-14)."""

from marshmallow import EXCLUDE, Schema, fields, validate

from app.constants.kots import ALLOWED_KOT_STATUSES


class UpdateKotStatusSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.String(
        required=True,
        validate=validate.OneOf(sorted(ALLOWED_KOT_STATUSES)),
    )


class UpdateKotItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=True)
    quantity = fields.Decimal(required=True, as_string=True, places=3)


class UpdateKotSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    notes = fields.String(load_default=None, allow_none=True)
    status = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(sorted(ALLOWED_KOT_STATUSES)),
    )
    items = fields.List(fields.Nested(UpdateKotItemSchema), load_default=None)


update_kot_status_schema = UpdateKotStatusSchema()
update_kot_schema = UpdateKotSchema()
