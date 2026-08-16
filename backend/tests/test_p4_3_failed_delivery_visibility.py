"""P4-3: WhatsApp delivery failure notifications."""

import hashlib
import hmac
import json
import uuid

from tests.conftest import login
from tests.test_p3_3_whatsapp_bill_delivery import _configure_whatsapp, _item


def _sign(body: bytes, secret: str = "test-app-secret") -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_webhook_failed_creates_notification(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _configure_whatsapp(client, owner)
    item = _item(client, owner, f"WA P43 {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9876522222",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    sent = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert sent.status_code == 200
    wamid = sent.get_json()["data"]["delivery"]["provider_message_id"]
    delivery_id = sent.get_json()["data"]["delivery"]["id"]

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "statuses": [
                                {
                                    "id": wamid,
                                    "status": "failed",
                                    "errors": [{"title": "User blocked"}],
                                }
                            ]
                        }
                    }
                ]
            }
        ],
    }
    raw = json.dumps(payload).encode()
    assert (
        client.post(
            "/api/v1/webhooks/whatsapp",
            data=raw,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": _sign(raw),
            },
        ).status_code
        == 200
    )

    notes = client.get(
        "/api/v1/notifications",
        headers=owner,
        query_string={"unread_only": True},
    ).get_json()["data"]
    wa = [n for n in notes if n["type"] == "WHATSAPP_DELIVERY_FAILED"]
    assert wa
    assert wa[0]["entity_id"] == delivery_id
    assert "User blocked" in wa[0]["message"]

    # Dedupe: second failed webhook should not create another unread for same delivery
    assert (
        client.post(
            "/api/v1/webhooks/whatsapp",
            data=raw,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": _sign(raw),
            },
        ).status_code
        == 200
    )
    notes2 = client.get(
        "/api/v1/notifications",
        headers=owner,
        query_string={"unread_only": True},
    ).get_json()["data"]
    assert (
        len([n for n in notes2 if n["type"] == "WHATSAPP_DELIVERY_FAILED" and n["entity_id"] == delivery_id])
        == 1
    )


def test_send_failure_creates_notification(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    # Configure with token that mock provider rejects
    client.put(
        "/api/v1/tenants/me/whatsapp",
        headers=owner,
        json={
            "phone_number_id": "pnid-111",
            "waba_id": "waba-222",
            "access_token": "fail-token",
            "template_name": "bill_receipt",
            "template_language": "en",
        },
    )
    item = _item(client, owner, f"WA P43 fail {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9876533333",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    failed = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert failed.status_code == 400

    notes = client.get("/api/v1/notifications", headers=owner).get_json()["data"]
    assert any(n["type"] == "WHATSAPP_DELIVERY_FAILED" for n in notes)
