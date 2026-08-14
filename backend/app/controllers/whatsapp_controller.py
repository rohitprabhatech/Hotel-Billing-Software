"""WhatsApp HTTP controllers."""

from flask import request

from app.schemas.whatsapp_schemas import (
    send_whatsapp_bill_schema,
    simulate_whatsapp_delivery_schema,
    whatsapp_config_schema,
)
from app.services.whatsapp_bill_service import WhatsappBillService
from app.services.whatsapp_config_service import WhatsappConfigService
from app.utils.responses import success_response


def get_whatsapp_config():
    return success_response(data=WhatsappConfigService.get_status())


def save_whatsapp_config():
    payload = whatsapp_config_schema.load(request.get_json() or {})
    data = WhatsappConfigService.save_config(
        phone_number_id=payload.get("phone_number_id"),
        waba_id=payload.get("waba_id"),
        access_token=payload.get("access_token"),
        display_phone=payload.get("display_phone"),
        template_name=payload.get("template_name"),
        template_language=payload.get("template_language"),
    )
    return success_response(data=data)


def test_whatsapp_config():
    return success_response(data=WhatsappConfigService.test_connection())


def disconnect_whatsapp_config():
    return success_response(data=WhatsappConfigService.disconnect())


def simulate_whatsapp_delivery():
    payload = simulate_whatsapp_delivery_schema.load(request.get_json() or {})
    data = WhatsappConfigService.simulate_delivery_status(
        provider_message_id=payload["provider_message_id"],
        status=payload["status"],
        error_message=payload.get("error_message"),
    )
    return success_response(data=data)


def send_bill_whatsapp(bill_id: str):
    payload = send_whatsapp_bill_schema.load(request.get_json() or {})
    data = WhatsappBillService.send_bill(
        bill_id,
        country_code=payload.get("country_code"),
        phone=payload.get("phone"),
        customer_name=payload.get("customer_name"),
    )
    return success_response(data=data)
