"""P4-2: WhatsApp failure visibility, list filter, mock simulator, FAILED audit."""

import hashlib
import hmac
import json
import uuid

from tests.conftest import login
from tests.test_p3_3_whatsapp_bill_delivery import _configure_whatsapp, _item


def _sign(body: bytes, secret: str = "test-app-secret") -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _send_bill(client, owner, billing):
    _configure_whatsapp(client, owner)
    item = _item(client, owner, f"WA P42 {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9876511111",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    sent = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert sent.status_code == 200
    delivery = sent.get_json()["data"]["delivery"]
    return bill, delivery


def test_webhook_failed_writes_audit_and_error(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    bill, delivery = _send_bill(client, owner, billing)
    wamid = delivery["provider_message_id"]

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
                                    "errors": [{"title": "Undeliverable"}],
                                }
                            ]
                        }
                    }
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

    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["whatsapp_delivery_status"] == "FAILED"
    latest = detail["deliveries"][0]
    assert latest["error_message"] == "Undeliverable"

    audits = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "BILL_WHATSAPP_FAILED", "per_page": 20},
    )
    assert audits.status_code == 200
    rows = audits.get_json()["data"]
    assert any(r.get("entity_id") == bill["id"] for r in rows)


def test_list_bills_whatsapp_status_filter(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    bill, delivery = _send_bill(client, owner, billing)

    listed = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"whatsapp_status": "SENT"},
    )
    assert listed.status_code == 200
    ids = {b["id"] for b in listed.get_json()["data"]}
    assert bill["id"] in ids

    empty = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"whatsapp_status": "FAILED"},
    )
    assert empty.status_code == 200
    assert bill["id"] not in {b["id"] for b in empty.get_json()["data"]}

    # Simulate delivered then filter
    sim = client.post(
        "/api/v1/tenants/me/whatsapp/simulate-delivery-status",
        headers=owner,
        json={
            "provider_message_id": delivery["provider_message_id"],
            "status": "delivered",
        },
    )
    assert sim.status_code == 200
    assert sim.get_json()["data"]["status"] == "DELIVERED"

    delivered = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"whatsapp_status": "DELIVERED"},
    )
    assert bill["id"] in {b["id"] for b in delivered.get_json()["data"]}


def test_simulate_failed_and_billing_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    bill, delivery = _send_bill(client, owner, billing)

    forbidden = client.post(
        "/api/v1/tenants/me/whatsapp/simulate-delivery-status",
        headers=billing,
        json={
            "provider_message_id": delivery["provider_message_id"],
            "status": "failed",
            "error_message": "Sim fail",
        },
    )
    assert forbidden.status_code == 403

    ok = client.post(
        "/api/v1/tenants/me/whatsapp/simulate-delivery-status",
        headers=owner,
        json={
            "provider_message_id": delivery["provider_message_id"],
            "status": "failed",
            "error_message": "Sim fail",
        },
    )
    assert ok.status_code == 200
    assert ok.get_json()["data"]["status"] == "FAILED"

    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["deliveries"][0]["error_message"] == "Sim fail"

    cfg = client.get("/api/v1/tenants/me/whatsapp", headers=owner).get_json()["data"]
    assert cfg.get("provider") == "mock"
