"""P5-3: Email delivery ops parity — notifications, filter, KPIs."""

import uuid
from unittest.mock import patch

from app.services.email_service import EmailService
from tests.conftest import login
from tests.test_p3_3_whatsapp_bill_delivery import _item


def test_email_send_failure_creates_notification_and_filter(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _item(client, owner, f"Email P53 {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_email": "fail@example.com",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]

    with patch.object(EmailService, "send_bill_pdf", side_effect=RuntimeError("SMTP down")):
        failed = client.post(
            f"/api/v1/bills/{bill['id']}/send-email",
            headers=billing,
            json={},
        )
    assert failed.status_code == 400

    notes = client.get(
        "/api/v1/notifications",
        headers=owner,
        query_string={"unread_only": True},
    ).get_json()["data"]
    email_notes = [n for n in notes if n["type"] == "EMAIL_DELIVERY_FAILED"]
    assert email_notes
    assert "SMTP down" in email_notes[0]["message"]

    listed = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"email_status": "FAILED"},
    )
    assert listed.status_code == 200
    assert bill["id"] in {b["id"] for b in listed.get_json()["data"]}


def test_report_summary_includes_email_delivery(client):
    EmailService.clear_outbox()
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _item(client, owner, f"Email P53 kpi {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_email": "kpi@example.com",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    sent = client.post(
        f"/api/v1/bills/{bill['id']}/send-email",
        headers=billing,
        json={},
    )
    assert sent.status_code == 200

    summary = client.get(
        "/api/v1/reports/summary",
        headers=owner,
        query_string={"period": "today"},
    )
    assert summary.status_code == 200
    email = summary.get_json()["data"]["email_delivery"]
    assert email["total"] >= 1
    assert email["sent"] >= 1
    assert email["success_rate"] is not None
    assert email["success_rate"] > 0
