"""Sprint BIZ-29 — serial / IMEI unit stock."""

from tests.conftest import login


def _switch_mobile(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "mobile"},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Mobile"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "15000",
        "gst_percentage": "18",
        "tracks_serial": True,
        "stock_quantity": "0",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_serial_receive_duplicate_blocked(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner)
    phone = _item(client, owner, cat_id, "Android Phone")

    received = client.post(
        "/api/v1/serial-units",
        headers=owner,
        json={"item_id": phone["id"], "serial": "IMEI12345678"},
    )
    assert received.status_code == 201, received.get_json()
    assert received.get_json()["data"]["status"] == "IN_STOCK"

    dup = client.post(
        "/api/v1/serial-units",
        headers=owner,
        json={"item_id": phone["id"], "serial": "imei12345678"},
    )
    assert dup.status_code == 409, dup.get_json()

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": phone["id"], "serial": "IMEI12345678", "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert bill.get_json()["data"]["items"][0]["serial_number"] == "IMEI12345678"

    resell = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": phone["id"], "serial": "IMEI12345678", "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert resell.status_code in {400, 409}, resell.get_json()


def test_serial_bill_requires_unit(client):
    billing = login(client, "billing@hotela.com", "Billing@12345")
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner, "Phones")
    phone = _item(client, owner, cat_id, "Feature Phone")
    denied = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": phone["id"], "quantity": 1}], "payment_method": "cash"},
    )
    assert denied.status_code == 400, denied.get_json()
