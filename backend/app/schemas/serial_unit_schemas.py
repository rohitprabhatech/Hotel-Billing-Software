"""Serial unit request schemas (BIZ-29)."""

from marshmallow import EXCLUDE, Schema, fields, validate


class ReceiveSerialSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    item_id = fields.String(required=True, validate=validate.Length(min=1, max=36))
    serial = fields.String(required=True, validate=validate.Length(min=4, max=64))


receive_serial_schema = ReceiveSerialSchema()
