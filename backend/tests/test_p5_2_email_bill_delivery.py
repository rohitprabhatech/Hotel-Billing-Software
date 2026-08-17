"""P5-2: Email PDF bill delivery."""

import uuid

from app.services.email_service import EmailService
from tests.conftest import login
from tests.test_p3_3_whatsapp_bill_delivery import _item


def test_send_bill_email_records_delivery_and_outbox(client):
    EmailService.clear_outbox()
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _item(client, owner, f"Email P52 {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_email": "customer@example.com",
            "customer_name": "Patil",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    assert bill["customer_email"] == "customer@example.com"

    sent = client.post(
        f"/api/v1/bills/{bill['id']}/send-email",
        headers=billing,
        json={},
    )
    assert sent.status_code == 200, sent.get_json()
    body = sent.get_json()["data"]
    assert body["delivery"]["status"] == "SENT"
    assert body["delivery"]["delivery_method"] == "EMAIL"
    assert body["bill"]["email_delivery_status"] == "SENT"

    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["email_delivery_status"] == "SENT"
    assert any(d["delivery_method"] == "EMAIL" for d in detail["deliveries"])

    outbox = EmailService.get_outbox()
    assert outbox
    last = outbox[-1]
    assert last["to"] == "customer@example.com"
    assert bill["bill_number"] in last["subject"]
    assert last["attachments"]
    assert last["attachments"][0]["filename"].endswith(".pdf")
    assert last["attachments"][0]["size"] > 0


def test_send_bill_email_requires_address(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _item(client, owner, f"Email P52 miss {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    missing = client.post(
        f"/api/v1/bills/{bill['id']}/send-email",
        headers=billing,
        json={},
    )
    assert missing.status_code == 400

    ok = client.post(
        f"/api/v1/bills/{bill['id']}/send-email",
        headers=billing,
        json={"email": "retry@example.com"},
    )
    assert ok.status_code == 200
    assert ok.get_json()["data"]["delivery"]["recipient_email_masked"]
