"""Owner WhatsApp Cloud API configuration (tenant-scoped)."""

from datetime import datetime, timezone

from flask import current_app

from app.extensions import db
from app.models.role import ROLE_OWNER
from app.models.tenant_whatsapp_config import TenantWhatsappConfig
from app.repositories.whatsapp_config_repository import WhatsappConfigRepository
from app.services.whatsapp_provider import get_whatsapp_provider
from app.utils.exceptions import ForbiddenError, ValidationError
from app.utils.phone import normalize_phone
from app.utils.request_context import require_request_context
from app.utils.secret_box import decrypt_secret, encrypt_secret


def _mask_id(value: str | None) -> str | None:
    if not value:
        return None
    v = str(value)
    if len(v) <= 6:
        return "*" * len(v)
    return f"{'*' * max(4, len(v) - 4)}{v[-4:]}"


class WhatsappConfigService:
    @staticmethod
    def _require_owner():
        ctx = require_request_context()
        if ctx.role != ROLE_OWNER:
            raise ForbiddenError("Only the business owner can manage WhatsApp settings.")
        return ctx

    @staticmethod
    def get_status():
        ctx = require_request_context()
        provider = current_app.config.get("WHATSAPP_PROVIDER") or "mock"
        row = WhatsappConfigRepository.get_by_tenant(ctx.tenant_id)
        if row is None:
            return {
                "status": "not_connected",
                "is_enabled": False,
                "has_token": False,
                "provider": provider,
                "phone_number_id_masked": None,
                "waba_id_masked": None,
                "display_phone_e164": None,
                "template_name": None,
                "template_language": "en",
                "connected_at": None,
            }
        connected = bool(row.is_enabled and row.access_token_encrypted and row.phone_number_id)
        return {
            "status": "connected" if connected else "not_connected",
            "is_enabled": bool(row.is_enabled),
            "has_token": bool(row.access_token_encrypted),
            "provider": provider,
            "phone_number_id_masked": _mask_id(row.phone_number_id),
            "waba_id_masked": _mask_id(row.waba_id),
            "display_phone_e164": row.display_phone_e164,
            "template_name": row.template_name,
            "template_language": row.template_language or "en",
            "connected_at": row.connected_at.isoformat() if row.connected_at else None,
        }

    @staticmethod
    def save_config(
        *,
        phone_number_id: str | None,
        waba_id: str | None,
        access_token: str | None,
        display_phone: str | None = None,
        template_name: str | None = None,
        template_language: str | None = None,
    ):
        ctx = WhatsappConfigService._require_owner()
        row = WhatsappConfigRepository.get_by_tenant(ctx.tenant_id)
        if row is None:
            row = TenantWhatsappConfig(tenant_id=ctx.tenant_id, template_language="en")
            WhatsappConfigRepository.upsert(row)

        pnid = (phone_number_id or "").strip() or None
        wid = (waba_id or "").strip() or None

        def _looks_masked(value: str | None) -> bool:
            if not value:
                return False
            return value.startswith("*") or set(value) <= {"*"}

        if pnid and not _looks_masked(pnid):
            row.phone_number_id = pnid
        if wid and not _looks_masked(wid):
            row.waba_id = wid

        if display_phone and str(display_phone).strip():
            try:
                parsed = normalize_phone(e164=str(display_phone).strip())
                row.display_phone_e164 = parsed["e164"]
            except ValidationError:
                row.display_phone_e164 = str(display_phone).strip()[:20]

        if template_name is not None:
            row.template_name = (template_name or "").strip() or None
        if template_language is not None:
            lang = (template_language or "en").strip() or "en"
            row.template_language = lang[:20]

        token = (access_token or "").strip()
        if token:
            row.access_token_encrypted = encrypt_secret(token)

        if not row.phone_number_id:
            raise ValidationError("Phone Number ID is required.")
        if not row.access_token_encrypted:
            raise ValidationError("Access token is required.")
        if not row.template_name:
            raise ValidationError("WhatsApp template name is required.")

        row.is_enabled = True
        row.connected_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.session.commit()
        return WhatsappConfigService.get_status()

    @staticmethod
    def disconnect():
        ctx = WhatsappConfigService._require_owner()
        row = WhatsappConfigRepository.get_by_tenant(ctx.tenant_id)
        if row is None:
            return WhatsappConfigService.get_status()
        row.is_enabled = False
        row.access_token_encrypted = None
        row.connected_at = None
        db.session.commit()
        return WhatsappConfigService.get_status()

    @staticmethod
    def test_connection():
        ctx = WhatsappConfigService._require_owner()
        row = WhatsappConfigRepository.get_by_tenant(ctx.tenant_id)
        if row is None or not row.access_token_encrypted or not row.phone_number_id:
            raise ValidationError("WhatsApp integration has not been configured for this business.")
        token = decrypt_secret(row.access_token_encrypted)
        provider = get_whatsapp_provider()
        result = provider.test_connection(access_token=token, phone_number_id=row.phone_number_id)
        if not result.success:
            raise ValidationError(result.error_message or "WhatsApp test connection failed.")
        display = None
        if result.raw and result.raw.get("display_phone_number"):
            display = result.raw["display_phone_number"]
            row.display_phone_e164 = str(display)[:20]
            db.session.commit()
        return {
            "ok": True,
            "message": "WhatsApp connection successful.",
            "display_phone": display or row.display_phone_e164,
        }

    @staticmethod
    def simulate_delivery_status(
        *,
        provider_message_id: str,
        status: str,
        error_message: str | None = None,
    ):
        ctx = WhatsappConfigService._require_owner()
        from app.repositories.bill_delivery_repository import BillDeliveryRepository
        from app.services.whatsapp_webhook_service import WhatsappWebhookService

        wamid = (provider_message_id or "").strip()
        if not wamid:
            raise ValidationError("provider_message_id is required.")
        row = BillDeliveryRepository.get_by_provider_message_id(wamid)
        if row is None or row.tenant_id != ctx.tenant_id:
            raise ValidationError("Unknown provider message id for this business.")

        result = WhatsappWebhookService.simulate_status(
            provider_message_id=wamid,
            meta_status=status,
            error_message=error_message,
        )
        if not result.get("updated"):
            reason = result.get("reason") or "no_change"
            if reason == "no_downgrade":
                raise ValidationError(
                    f"Cannot change delivery status from {result.get('status')} to {status}."
                )
            raise ValidationError("Delivery status was not updated.")
        return result

    @staticmethod
    def require_ready_config(tenant_id: str) -> TenantWhatsappConfig:
        row = WhatsappConfigRepository.get_by_tenant(tenant_id)
        if (
            row is None
            or not row.is_enabled
            or not row.access_token_encrypted
            or not row.phone_number_id
            or not row.template_name
        ):
            raise ValidationError(
                "WhatsApp integration has not been configured for this business. Please contact your Business Owner."
            )
        return row
