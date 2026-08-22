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


update_kot_status_schema = UpdateKotStatusSchema()
