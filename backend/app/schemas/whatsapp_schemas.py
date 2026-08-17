"""WhatsApp / bill delivery request schemas."""

from marshmallow import EXCLUDE, Schema, fields, validate


class SendWhatsappBillSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    country_code = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=8)
    )
    phone = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=20))
    customer_name = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=120)
    )


class WhatsappConfigSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    phone_number_id = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=64)
    )
    waba_id = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=64))
    access_token = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=4000)
    )
    display_phone = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=20)
    )
    template_name = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=120)
    )
    template_language = fields.String(
        load_default="en", allow_none=True, validate=validate.Length(max=20)
    )


class SimulateWhatsappDeliverySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    provider_message_id = fields.String(required=True, validate=validate.Length(min=1, max=128))
    status = fields.String(
        required=True,
        validate=validate.OneOf(["sent", "delivered", "read", "failed"]),
    )
    error_message = fields.String(
        load_default=None, allow_none=True, validate=validate.Length(max=500)
    )


send_whatsapp_bill_schema = SendWhatsappBillSchema()
whatsapp_config_schema = WhatsappConfigSchema()
simulate_whatsapp_delivery_schema = SimulateWhatsappDeliverySchema()
