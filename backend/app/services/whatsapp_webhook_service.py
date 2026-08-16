"""Meta WhatsApp Cloud API delivery status webhooks."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone

from flask import current_app

from app.extensions import db
from app.repositories.bill_delivery_repository import BillDeliveryRepository
from app.services.audit_service import AuditService

# Progression: PENDING < SENT < DELIVERED < READ
# FAILED may replace PENDING/SENT only (not after delivered/read).
_STATUS_RANK = {
    "PENDING": 0,
    "SENT": 1,
    "FAILED": 1,
    "DELIVERED": 2,
    "READ": 3,
}

_META_TO_STATUS = {
    "sent": "SENT",
    "delivered": "DELIVERED",
    "read": "READ",
    "failed": "FAILED",
}


class WhatsappWebhookService:
    @staticmethod
    def verify_challenge(*, mode: str | None, token: str | None, challenge: str | None):
        expected = current_app.config.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN") or ""
        if mode == "subscribe" and expected and token == expected and challenge is not None:
            return str(challenge)
        return None

    @staticmethod
    def signature_valid(raw_body: bytes, signature_header: str | None) -> bool:
        secret = current_app.config.get("WHATSAPP_APP_SECRET") or ""
        if not secret:
            # In mock/dev without secret, accept only when provider is mock
            return (current_app.config.get("WHATSAPP_PROVIDER") or "mock") == "mock"
        if not signature_header or not signature_header.startswith("sha256="):
            return False
        digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        offered = signature_header.split("=", 1)[1].strip()
        return hmac.compare_digest(digest, offered)

    @staticmethod
    def _may_apply(current: str, incoming: str) -> bool:
        if incoming == current:
            return False
        if incoming == "FAILED":
            return current in {"PENDING", "SENT"}
        return _STATUS_RANK.get(incoming, -1) > _STATUS_RANK.get(current, -1)

    @staticmethod
    def apply_meta_status(
        *,
        provider_message_id: str,
        meta_status: str,
        errors=None,
        source: str = "webhook",
    ) -> dict:
        mapped = _META_TO_STATUS.get((meta_status or "").lower())
        if not mapped or not provider_message_id:
            return {"updated": False, "reason": "ignored"}

        row = BillDeliveryRepository.get_by_provider_message_id(provider_message_id)
        if row is None:
            return {"updated": False, "reason": "unknown_wamid"}

        if not WhatsappWebhookService._may_apply(row.status, mapped):
            return {
                "updated": False,
                "reason": "no_downgrade",
                "status": row.status,
                "delivery_id": row.id,
            }

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        row.status = mapped
        if mapped == "SENT" and not row.sent_at:
            row.sent_at = now
        if mapped == "DELIVERED":
            row.delivered_at = now
            if not row.sent_at:
                row.sent_at = now
        if mapped == "READ":
            row.read_at = now
            if not row.delivered_at:
                row.delivered_at = now
            if not row.sent_at:
                row.sent_at = now
        if mapped == "FAILED":
            if errors:
                try:
                    msg = errors[0].get("title") or errors[0].get("message") or str(errors[0])
                except Exception:
                    msg = "WhatsApp delivery failed"
                row.error_message = str(msg)[:500]
            else:
                row.error_message = row.error_message or "WhatsApp delivery failed"
            AuditService.log(
                tenant_id=row.tenant_id,
                action="BILL_WHATSAPP_FAILED",
                entity_type="bill",
                entity_id=row.bill_id,
                user_id=None,
                user_name="WhatsApp webhook" if source == "webhook" else "WhatsApp simulator",
                new_data={
                    "delivery_id": row.id,
                    "error_message": row.error_message,
                    "source": source,
                    "provider_message_id": row.provider_message_id,
                },
            )
            from app.repositories.bill_repository import BillRepository
            from app.services.notification_service import NotificationService

            bill = BillRepository.get_by_id_and_tenant(row.bill_id, row.tenant_id)
            NotificationService.notify_whatsapp_delivery_failed(
                tenant_id=row.tenant_id,
                bill_id=row.bill_id,
                delivery_id=row.id,
                bill_number=bill.bill_number if bill else None,
                error_message=row.error_message,
                recipient_masked=row.recipient_phone_masked,
            )

        db.session.commit()
        return {
            "updated": True,
            "delivery_id": row.id,
            "bill_id": row.bill_id,
            "tenant_id": row.tenant_id,
            "status": row.status,
            "error_message": row.error_message,
        }

    @staticmethod
    def ingest_payload(payload: dict) -> dict:
        """Parse Meta webhook JSON; apply all status objects found."""
        results = []
        for entry in payload.get("entry") or []:
            for change in entry.get("changes") or []:
                value = change.get("value") or {}
                for st in value.get("statuses") or []:
                    results.append(
                        WhatsappWebhookService.apply_meta_status(
                            provider_message_id=st.get("id") or "",
                            meta_status=st.get("status") or "",
                            errors=st.get("errors"),
                            source="webhook",
                        )
                    )
        return {"processed": len(results), "results": results}

    @staticmethod
    def simulate_status(
        *,
        provider_message_id: str,
        meta_status: str,
        error_message: str | None = None,
    ) -> dict:
        """Owner-only mock helper — same status rules as Meta webhook."""
        if (current_app.config.get("WHATSAPP_PROVIDER") or "mock") != "mock":
            from app.utils.exceptions import ForbiddenError

            raise ForbiddenError(
                "Delivery status simulator is only available when WHATSAPP_PROVIDER=mock."
            )
        errors = None
        if (meta_status or "").lower() == "failed":
            errors = [{"title": (error_message or "Simulated WhatsApp failure")[:500]}]
        return WhatsappWebhookService.apply_meta_status(
            provider_message_id=provider_message_id,
            meta_status=meta_status,
            errors=errors,
            source="simulator",
        )
