"""P4-1: WhatsApp delivery status webhooks."""

import hashlib
import hmac
import json

from tests.conftest import login
from tests.test_p3_3_whatsapp_bill_delivery import _configure_whatsapp, _item


def _sign(body: bytes, secret: str = "test-app-secret") -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_webhook_verify_challenge(client):
    ok = client.get(
        "/api/v1/webhooks/whatsapp",
        query_string={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": "12345",
        },
    )
    assert ok.status_code == 200
    assert ok.data.decode() == "12345"

    bad = client.get(
        "/api/v1/webhooks/whatsapp",
        query_string={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "12345",
        },
    )
    assert bad.status_code == 403


def test_webhook_rejects_bad_signature(client):
    body = json.dumps({"object": "whatsapp_business_account", "entry": []}).encode()
    res = client.post(
        "/api/v1/webhooks/whatsapp",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=deadbeef",
        },
    )
    assert res.status_code == 403


def test_webhook_status_progression_and_no_downgrade(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _configure_whatsapp(client, owner)
    item = _item(client, owner, "WA Hook Item")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9876512345",
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
    assert wamid

    def post_status(status):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [{"id": wamid, "status": status, "timestamp": "1"}]
                            }
                        }
                    ]
                }
            ],
        }
        raw = json.dumps(payload).encode()
        return client.post(
            "/api/v1/webhooks/whatsapp",
            data=raw,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": _sign(raw),
            },
        )

    assert post_status("delivered").status_code == 200
    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["whatsapp_delivery_status"] == "DELIVERED"

    assert post_status("read").status_code == 200
    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["whatsapp_delivery_status"] == "READ"

    # No downgrade to sent
    assert post_status("sent").status_code == 200
    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["whatsapp_delivery_status"] == "READ"


def test_webhook_unknown_wamid_noop(client):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {"value": {"statuses": [{"id": "unknown-wamid", "status": "delivered"}]}}
                ]
            }
        ],
    }
    raw = json.dumps(payload).encode()
    res = client.post(
        "/api/v1/webhooks/whatsapp",
        data=raw,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign(raw),
        },
    )
    assert res.status_code == 200
    body = res.get_json()["data"]
    assert body["processed"] == 1
    assert body["results"][0]["reason"] == "unknown_wamid"
