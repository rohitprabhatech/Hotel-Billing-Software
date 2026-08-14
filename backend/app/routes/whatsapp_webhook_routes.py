"""Public WhatsApp Cloud API webhook endpoints."""

from flask import Blueprint

from app.controllers import whatsapp_webhook_controller

whatsapp_webhook_bp = Blueprint(
    "whatsapp_webhook", __name__, url_prefix="/webhooks/whatsapp"
)


@whatsapp_webhook_bp.get("")
def verify_webhook():
    return whatsapp_webhook_controller.verify_webhook()


@whatsapp_webhook_bp.post("")
def receive_webhook():
    return whatsapp_webhook_controller.receive_webhook()
