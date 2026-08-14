"""P3-3: WhatsApp bill delivery — mock provider, isolation, no duplicate bills."""

from tests.conftest import login


def _item(client, headers, name="WA Item"):
    cat = client.post(
        "/api/v1/categories", headers=headers, json={"name": f"Cat-{name}"}
    ).get_json()["data"]["id"]
    return client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": name,
            "category_id": cat,
            "price": 100,
            "gst_percentage": 0,
            "stock_quantity": None,
        },
    ).get_json()["data"]


def _configure_whatsapp(client, headers, *, token="good-token"):
    res = client.put(
        "/api/v1/tenants/me/whatsapp",
        headers=headers,
        json={
            "phone_number_id": "pnid-111",
            "waba_id": "waba-222",
            "access_token": token,
            "template_name": "bill_receipt",
            "template_language": "en",
        },
    )
    assert res.status_code == 200, res.get_json()
    body = res.get_json()["data"]
    assert body["status"] == "connected"
    assert body["has_token"] is True
    assert "good-token" not in str(body)
    assert "access_token" not in body
    return body


def test_whatsapp_config_never_returns_token(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _configure_whatsapp(client, owner)
    status = client.get("/api/v1/tenants/me/whatsapp", headers=owner).get_json()["data"]
    assert status["has_token"] is True
    assert "access_token" not in status
    assert status["phone_number_id_masked"]


def test_whatsapp_tenant_isolation_config(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _configure_whatsapp(client, owner_a, token="tenant-a-secret")
    status_b = client.get("/api/v1/tenants/me/whatsapp", headers=owner_b).get_json()["data"]
    assert status_b["status"] == "not_connected"
    assert status_b["has_token"] is False


def test_send_whatsapp_success_no_duplicate_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _configure_whatsapp(client, owner)
    item = _item(client, owner, "WA Success")

    created = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_name": "Rahul Patil",
            "customer_phone_country_code": "91",
            "customer_phone": "9876543210",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    )
    assert created.status_code == 201, created.get_json()
    bill = created.get_json()["data"]
    bill_id = bill["id"]
    bill_number = bill["bill_number"]
    assert bill["customer_phone_masked"]
    assert "***" in bill["customer_phone_masked"] or "******" in bill["customer_phone_masked"]

    sent = client.post(
        f"/api/v1/bills/{bill_id}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert sent.status_code == 200, sent.get_json()
    assert "successfully" in sent.get_json()["data"]["message"].lower()
    assert sent.get_json()["data"]["delivery"]["status"] == "SENT"

    # Retry does not create another bill
    again = client.post(
        f"/api/v1/bills/{bill_id}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert again.status_code == 200

    listed = client.get("/api/v1/bills", headers=owner).get_json()["data"]
    matching = [b for b in listed if b["bill_number"] == bill_number]
    assert len(matching) == 1
    assert matching[0]["whatsapp_delivery_status"] == "SENT"
    assert matching[0]["grand_total"] == bill["grand_total"]


def test_send_whatsapp_failure_keeps_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _configure_whatsapp(client, owner, token="force-fail-token")
    item = _item(client, owner, "WA Fail")

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "online",
            "customer_phone_country_code": "91",
            "customer_phone": "9123456789",
            "items": [{"item_id": item["id"], "quantity": 2}],
        },
    ).get_json()["data"]

    failed = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert failed.status_code == 400
    assert "WhatsApp" in failed.get_json()["error"]["message"]

    still = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert still["status"] == "FINALIZED"
    assert still["grand_total"] == bill["grand_total"]
    assert still["whatsapp_delivery_status"] == "FAILED"


def test_send_without_config_clear_message(client):
    billing = login(client, "billing@hotela.com", "Billing@12345")
    owner = login(client, "owner@hotela.com", "Owner@12345")
    item = _item(client, owner, "WA NoConfig")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9000000001",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]

    res = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
        headers=billing,
        json={},
    )
    assert res.status_code == 400
    assert "not been configured" in res.get_json()["error"]["message"].lower()


def test_tenant_b_cannot_send_tenant_a_bill(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    billing_a = login(client, "billing@hotela.com", "Billing@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _configure_whatsapp(client, owner_a)
    _configure_whatsapp(client, owner_b, token="tenant-b-token")
    item = _item(client, owner_a, "WA Cross")
    bill = client.post(
        "/api/v1/bills",
        headers=billing_a,
        json={
            "payment_method": "cash",
            "customer_phone_country_code": "91",
            "customer_phone": "9888888888",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]

    cross = client.post(
        f"/api/v1/bills/{bill['id']}/send-whatsapp",
        headers=owner_b,
        json={},
    )
    assert cross.status_code == 404
