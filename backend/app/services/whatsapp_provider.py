"""Official WhatsApp Cloud API providers (mock + Meta Graph)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from flask import current_app

from app.utils.exceptions import AppError


class WhatsAppProviderError(AppError):
    status_code = 502
    code = "WHATSAPP_PROVIDER_ERROR"


@dataclass
class WhatsAppSendResult:
    success: bool
    provider_message_id: str | None = None
    error_message: str | None = None
    raw: dict | None = None


class MockWhatsAppProvider:
    """CI / local provider — no network. Fail if token contains 'fail' (case-insensitive)."""

    def send_bill_document(
        self,
        *,
        access_token: str,
        phone_number_id: str,
        recipient_e164: str,
        template_name: str,
        template_language: str,
        pdf_bytes: bytes,
        filename: str,
        body_params: list[str],
    ) -> WhatsAppSendResult:
        _ = (phone_number_id, recipient_e164, template_name, template_language, pdf_bytes, filename, body_params)
        if "fail" in (access_token or "").lower():
            return WhatsAppSendResult(
                success=False,
                error_message="Unable to send the bill on WhatsApp. Please try again or use Print Bill.",
            )
        return WhatsAppSendResult(
            success=True,
            provider_message_id="mock-wamid-success",
            raw={"mock": True},
        )

    def test_connection(self, *, access_token: str, phone_number_id: str) -> WhatsAppSendResult:
        if "fail" in (access_token or "").lower():
            return WhatsAppSendResult(success=False, error_message="WhatsApp test connection failed.")
        if not access_token or not phone_number_id:
            return WhatsAppSendResult(success=False, error_message="Missing WhatsApp credentials.")
        return WhatsAppSendResult(success=True, provider_message_id="mock-ok")


class MetaWhatsAppProvider:
    """WhatsApp Cloud API (Graph) — document upload + template send."""

    def _graph_base(self) -> str:
        version = current_app.config.get("WHATSAPP_GRAPH_API_VERSION", "v21.0")
        return f"https://graph.facebook.com/{version}"

    def _request_json(self, method: str, url: str, *, token: str, data=None, content_type=None):
        headers = {"Authorization": f"Bearer {token}"}
        body = None
        if data is not None:
            if content_type == "application/json":
                body = json.dumps(data).encode("utf-8")
                headers["Content-Type"] = "application/json"
            else:
                body = data
                if content_type:
                    headers["Content-Type"] = content_type
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            raise WhatsAppProviderError(
                "WhatsApp service is temporarily unavailable. Please try again or print the bill.",
                details={"http_status": exc.code, "provider": detail[:500]},
            ) from exc
        except urllib.error.URLError as exc:
            raise WhatsAppProviderError(
                "WhatsApp service is temporarily unavailable. Please try again or print the bill."
            ) from exc

    def test_connection(self, *, access_token: str, phone_number_id: str) -> WhatsAppSendResult:
        url = f"{self._graph_base()}/{phone_number_id}?fields=display_phone_number,verified_name"
        data = self._request_json("GET", url, token=access_token)
        return WhatsAppSendResult(
            success=True,
            provider_message_id=str(data.get("id") or phone_number_id),
            raw={"display_phone_number": data.get("display_phone_number")},
        )

    def send_bill_document(
        self,
        *,
        access_token: str,
        phone_number_id: str,
        recipient_e164: str,
        template_name: str,
        template_language: str,
        pdf_bytes: bytes,
        filename: str,
        body_params: list[str],
    ) -> WhatsAppSendResult:
        # 1) Upload media
        boundary = "----bbsBoundary7MA4YWxkTrZu0gW"
        to = recipient_e164.lstrip("+")
        multipart = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="messaging_product"\r\n\r\nwhatsapp\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="type"\r\n\r\napplication/pdf\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: application/pdf\r\n\r\n"
        ).encode("utf-8") + pdf_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

        upload_url = f"{self._graph_base()}/{phone_number_id}/media"
        upload = self._request_json(
            "POST",
            upload_url,
            token=access_token,
            data=multipart,
            content_type=f"multipart/form-data; boundary={boundary}",
        )
        media_id = upload.get("id")
        if not media_id:
            raise WhatsAppProviderError(
                "Unable to upload the bill PDF to WhatsApp. Please try again or use Print Bill."
            )

        # 2) Send template with document header when possible
        components = [
            {
                "type": "header",
                "parameters": [
                    {
                        "type": "document",
                        "document": {"id": media_id, "filename": filename},
                    }
                ],
            }
        ]
        if body_params:
            components.append(
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in body_params],
                }
            )

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": template_language or "en"},
                "components": components,
            },
        }
        send_url = f"{self._graph_base()}/{phone_number_id}/messages"
        sent = self._request_json(
            "POST",
            send_url,
            token=access_token,
            data=payload,
            content_type="application/json",
        )
        messages = sent.get("messages") or []
        wamid = messages[0].get("id") if messages else None
        return WhatsAppSendResult(success=True, provider_message_id=wamid, raw=sent)


def get_whatsapp_provider():
    name = (current_app.config.get("WHATSAPP_PROVIDER") or "mock").lower()
    if name == "meta":
        return MetaWhatsAppProvider()
    return MockWhatsAppProvider()
