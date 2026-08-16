"""P4-4: WhatsApp delivery analytics on report summary."""

import uuid

from tests.conftest import login
from tests.test_p3_3_whatsapp_bill_delivery import _configure_whatsapp, _item


def test_report_summary_includes_whatsapp_delivery(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _configure_whatsapp(client, owner)
    item = _item(client, owner, f"WA P44 {uuid.uuid4().hex[:8]}")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9876544444",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    sent = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
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
    wa = summary.get_json()["data"]["whatsapp_delivery"]
    assert wa["total"] >= 1
    assert wa["sent"] >= 1
    assert "success_rate" in wa
    assert "pending" in wa
    assert "delivered" in wa
    assert "read" in wa
    assert "failed" in wa

    # Advance to delivered via simulator — success_rate should become > 0
    wamid = sent.get_json()["data"]["delivery"]["provider_message_id"]
    sim = client.post(
        "/api/v1/tenants/me/whatsapp/simulate-delivery-status",
        headers=owner,
        json={"provider_message_id": wamid, "status": "delivered"},
    )
    assert sim.status_code == 200

    summary2 = client.get(
        "/api/v1/reports/summary",
        headers=owner,
        query_string={"period": "today"},
    ).get_json()["data"]["whatsapp_delivery"]
    assert summary2["delivered"] >= 1
    assert summary2["success_rate"] is not None
    assert summary2["success_rate"] > 0
