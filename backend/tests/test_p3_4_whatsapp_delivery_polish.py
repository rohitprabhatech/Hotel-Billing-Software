"""P3-4: WhatsApp delivery polish — delivery history on bill detail."""

from tests.conftest import login
from tests.test_p3_3_whatsapp_bill_delivery import _configure_whatsapp, _item


def test_get_bill_includes_delivery_attempts(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _configure_whatsapp(client, owner)
    item = _item(client, owner, "WA History")

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9876501234",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]

    sent = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert sent.status_code == 200

    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["whatsapp_delivery_status"] == "SENT"
    assert isinstance(detail.get("deliveries"), list)
    assert len(detail["deliveries"]) >= 1
    assert detail["deliveries"][0]["delivery_method"] == "WHATSAPP"
    assert detail["deliveries"][0]["status"] == "SENT"
    assert detail["deliveries"][0]["recipient_phone_masked"]
    # Full phone must not appear in masked field
    assert "9876501234" not in (detail["deliveries"][0]["recipient_phone_masked"] or "")
