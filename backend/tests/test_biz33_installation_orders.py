"""Sprint BIZ-33 — electronics installation jobs linked to serial sales."""

from datetime import datetime, timedelta

from tests.conftest import login


def _switch_electronics(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "electronics"},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Electronics"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "25000",
        "gst_percentage": "18",
        "tracks_serial": True,
        "stock_quantity": "0",
        "uom": "pcs",
        "brand": "LG",
        "model_name": "Split AC 1.5T",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_installation_lifecycle_linked_to_serial_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_electronics(client, owner)
    cat_id = _category(client, owner)
    ac = _item(client, owner, cat_id, "Split AC")

    unit = client.post(
        "/api/v1/serial-units",
        headers=owner,
        json={"item_id": ac["id"], "serial": "SNINSTALL3301"},
    )
    assert unit.status_code == 201, unit.get_json()
    unit_id = unit.get_json()["data"]["id"]

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": ac["id"], "serial": "SNINSTALL3301", "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_id = bill.get_json()["data"]["id"]

    denied = client.post(
        "/api/v1/installations",
        headers=billing,
        json={
            "serial_unit_id": unit_id,
            "scheduled_at": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00"),
        },
    )
    assert denied.status_code == 403, denied.get_json()

    scheduled = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00")
    created = client.post(
        "/api/v1/installations",
        headers=owner,
        json={
            "serial_unit_id": unit_id,
            "scheduled_at": scheduled,
            "install_address": "12 MG Road",
            "customer_name": "Suresh",
            "technician_name": "Ravi Tech",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["status"] == "SCHEDULED"
    assert body["serial"] == "SNINSTALL3301"
    assert body["bill_id"] == bill_id
    installation_id = body["id"]

    notifications = client.get("/api/v1/notifications", headers=owner)
    assert notifications.status_code == 200, notifications.get_json()
    types = {row["type"] for row in notifications.get_json()["data"]}
    assert "INSTALLATION_SCHEDULED" in types

    started = client.patch(
        f"/api/v1/installations/{installation_id}/status",
        headers=owner,
        json={"status": "IN_PROGRESS"},
    )
    assert started.status_code == 200, started.get_json()

    done = client.patch(
        f"/api/v1/installations/{installation_id}/status",
        headers=owner,
        json={"status": "COMPLETED"},
    )
    assert done.status_code == 200, done.get_json()
    assert done.get_json()["data"]["completed_at"] is not None

    notifications2 = client.get("/api/v1/notifications", headers=owner)
    types2 = {row["type"] for row in notifications2.get_json()["data"]}
    assert "INSTALLATION_COMPLETED" in types2

    listing = client.get("/api/v1/installations", headers=owner)
    assert listing.status_code == 200, listing.get_json()
    assert any(row["id"] == installation_id for row in listing.get_json()["data"])


def test_mobile_installations_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=owner,
        json={"business_type": "mobile"},
    )
    denied = client.get("/api/v1/installations", headers=owner)
    assert denied.status_code == 403


def test_restaurant_installations_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    denied = client.get("/api/v1/installations", headers=headers)
    assert denied.status_code == 403
