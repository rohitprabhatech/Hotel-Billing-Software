"""WhatsApp webhook HTTP handlers (public — signature verified)."""

from flask import Response, current_app, request

from app.services.whatsapp_webhook_service import WhatsappWebhookService
from app.utils.responses import error_response, success_response


def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    result = WhatsappWebhookService.verify_challenge(
        mode=mode, token=token, challenge=challenge
    )
    if result is None:
        return error_response("Webhook verification failed", status_code=403, code="FORBIDDEN")
    return Response(result, status=200, mimetype="text/plain")


def receive_webhook():
    raw = request.get_data() or b""
    signature = request.headers.get("X-Hub-Signature-256")
    if not WhatsappWebhookService.signature_valid(raw, signature):
        current_app.logger.warning("WhatsApp webhook signature rejected")
        return error_response("Invalid signature", status_code=403, code="FORBIDDEN")

    payload = request.get_json(silent=True) or {}
    data = WhatsappWebhookService.ingest_payload(payload)
    return success_response(data=data)
