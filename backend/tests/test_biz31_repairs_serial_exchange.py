"""Sprint BIZ-31 — serial return/quarantine, exchange, and repair tickets."""

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


def _receive(client, headers, item_id, serial):
    response = client.post(
        "/api/v1/serial-units",
        headers=headers,
        json={"item_id": item_id, "serial": serial},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _sell(client, headers, item_id, serial):
    response = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "items": [{"item_id": item_id, "serial": serial, "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_serial_return_restock_and_quarantine(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner)
    phone = _item(client, owner, cat_id, "Return Phone")
    unit = _receive(client, owner, phone["id"], "SNRETURN01")
    bill = _sell(client, billing, phone["id"], "SNRETURN01")
    line = bill["items"][0]

    created = client.post(
        "/api/v1/returns",
        headers=owner,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Customer changed mind",
            "items": [{"bill_item_id": line["id"], "quantity": "1", "quarantine": False}],
        },
    )
    assert created.status_code == 201, created.get_json()

    listed = client.get("/api/v1/serial-units", headers=owner, query_string={"q": "SNRETURN01"})
    assert listed.status_code == 200, listed.get_json()
    assert listed.get_json()["data"][0]["status"] == "IN_STOCK"

    bill2 = _sell(client, billing, phone["id"], "SNRETURN01")
    line2 = bill2["items"][0]
    quarantined = client.post(
        "/api/v1/returns",
        headers=owner,
        json={
            "bill_id": bill2["id"],
            "kind": "RETURN",
            "reason": "Faulty device",
            "items": [{"bill_item_id": line2["id"], "quantity": "1", "quarantine": True}],
        },
    )
    assert quarantined.status_code == 201, quarantined.get_json()
    listed2 = client.get("/api/v1/serial-units", headers=owner, query_string={"q": "SNRETURN01"})
    assert listed2.status_code == 200, listed2.get_json()
    row = listed2.get_json()["data"][0]
    assert row["status"] == "QUARANTINE"


def test_serial_exchange_swaps_imei_on_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner)
    phone = _item(client, owner, cat_id, "Exchange Phone")
    old = _receive(client, owner, phone["id"], "SNOLD0001")
    new = _receive(client, owner, phone["id"], "SNNEW0002")
    bill = _sell(client, billing, phone["id"], "SNOLD0001")
    line = bill["items"][0]

    exchanged = client.post(
        "/api/v1/returns",
        headers=owner,
        json={
            "bill_id": bill["id"],
            "kind": "EXCHANGE",
            "reason": "Dead on arrival",
            "items": [
                {
                    "bill_item_id": line["id"],
                    "quantity": "1",
                    "exchange_serial_unit_id": new["id"],
                }
            ],
        },
    )
    assert exchanged.status_code == 201, exchanged.get_json()

    bill_view = client.get(f"/api/v1/bills/{bill['id']}", headers=owner)
    assert bill_view.status_code == 200, bill_view.get_json()
    assert bill_view.get_json()["data"]["items"][0]["serial_number"] == "SNNEW0002"

    units = {
        row["serial"]: row["status"]
        for row in client.get("/api/v1/serial-units", headers=owner, query_string={"item_id": phone["id"]}).get_json()[
            "data"
        ]
    }
    assert units["SNOLD0001"] == "QUARANTINE"
    assert units["SNNEW0002"] == "SOLD"


def test_repair_ticket_lifecycle(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner)
    phone = _item(client, owner, cat_id, "Repair Phone")
    unit = _receive(client, owner, phone["id"], "SNREPAIR01")
    _sell(client, billing, phone["id"], "SNREPAIR01")

    denied = client.post(
        "/api/v1/repairs",
        headers=billing,
        json={"serial_unit_id": unit["id"], "issue_description": "Screen cracked"},
    )
    assert denied.status_code == 403, denied.get_json()

    created = client.post(
        "/api/v1/repairs",
        headers=owner,
        json={
            "serial_unit_id": unit["id"],
            "issue_description": "Screen cracked",
            "customer_name": "Ravi",
            "estimated_charge": "1200",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    repair_id = body["id"]
    assert body["status"] == "RECEIVED"
    assert body["serial"] == "SNREPAIR01"

    progressed = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers=owner,
        json={"status": "IN_PROGRESS"},
    )
    assert progressed.status_code == 200, progressed.get_json()

    ready = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers=owner,
        json={"status": "READY"},
    )
    assert ready.status_code == 200, ready.get_json()
    assert ready.get_json()["data"]["status"] == "READY"

    notifications = client.get("/api/v1/notifications", headers=owner)
    assert notifications.status_code == 200, notifications.get_json()
    types = {row["type"] for row in notifications.get_json()["data"]}
    assert "REPAIR_READY" in types

    delivered = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers=owner,
        json={"status": "DELIVERED"},
    )
    assert delivered.status_code == 200, delivered.get_json()
    assert delivered.get_json()["data"]["delivered_at"] is not None


def test_restaurant_repairs_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    denied = client.get("/api/v1/repairs", headers=headers)
    assert denied.status_code == 403
