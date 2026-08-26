"""Sprint BIZ-49 — furniture delivery board and installation from custom orders."""

from datetime import datetime, timedelta

from tests.conftest import login


def _switch_furniture(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "furniture"},
    )
    assert response.status_code == 200, response.get_json()


def _create_ready_order(client, headers, *, title="Wardrobe", address="12 MG Road"):
    delivery = (datetime.utcnow() + timedelta(days=5)).isoformat()
    created = client.post(
        "/api/v1/furniture/custom-orders",
        headers=headers,
        json={
            "title": title,
            "size": "180×60×210",
            "flavor": "Teak",
            "customer_name": "Priya",
            "customer_phone": "9000000049",
            "total_amount": "35000",
            "advance_amount": "10000",
            "delivery_at": delivery,
        },
    )
    assert created.status_code == 201, created.get_json()
    oid = created.get_json()["data"]["id"]
    manager = login(client, "manager@hotela.com", "Manager@12345")
    for status in ("CONFIRMED", "IN_PRODUCTION", "READY"):
        updated = client.patch(
            f"/api/v1/custom-orders/{oid}/status",
            headers=manager,
            json={"status": status},
        )
        assert updated.status_code == 200, updated.get_json()
    return oid


def test_delivery_module_forbidden_for_restaurant(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=owner,
        json={"business_type": "hotel_restaurant"},
    )
    assert client.get("/api/v1/deliveries", headers=owner).status_code == 403


def test_furniture_cannot_mark_delivered_directly(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_furniture(client, owner)
    oid = _create_ready_order(client, billing)

    blocked = client.patch(
        f"/api/v1/custom-orders/{oid}/status",
        headers=owner,
        json={"status": "DELIVERED"},
    )
    assert blocked.status_code == 400, blocked.get_json()
    assert "delivery board" in blocked.get_json()["error"]["message"].lower()


def test_delivery_lifecycle_and_notifications(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_furniture(client, owner)
    oid = _create_ready_order(client, billing)

    denied = client.post(
        "/api/v1/deliveries",
        headers=billing,
        json={
            "custom_order_id": oid,
            "delivery_address": "Flat 4, Lake View Apartments",
        },
    )
    assert denied.status_code == 403, denied.get_json()

    scheduled = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%dT14:00:00")
    created = client.post(
        "/api/v1/furniture/deliveries",
        headers=owner,
        json={
            "custom_order_id": oid,
            "delivery_address": "Flat 4, Lake View Apartments",
            "scheduled_at": scheduled,
            "driver_name": "Ramesh",
            "vehicle_number": "MH12AB1234",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["delivery_number"].startswith("DL-")
    assert body["status"] == "SCHEDULED"
    assert body["custom_order_id"] == oid
    did = body["id"]

    dup = client.post(
        "/api/v1/deliveries",
        headers=owner,
        json={
            "custom_order_id": oid,
            "delivery_address": "Another address",
        },
    )
    assert dup.status_code == 400, dup.get_json()

    out = client.patch(
        f"/api/v1/deliveries/{did}/status",
        headers=owner,
        json={"status": "OUT_FOR_DELIVERY"},
    )
    assert out.status_code == 200, out.get_json()
    assert out.get_json()["data"]["status"] == "OUT_FOR_DELIVERY"
    assert out.get_json()["data"]["out_for_delivery_at"]

    done = client.patch(
        f"/api/v1/deliveries/{did}/status",
        headers=owner,
        json={"status": "DELIVERED"},
    )
    assert done.status_code == 200, done.get_json()
    assert done.get_json()["data"]["status"] == "DELIVERED"
    assert done.get_json()["data"]["delivered_at"]

    order = client.get(f"/api/v1/custom-orders/{oid}", headers=owner)
    assert order.status_code == 200, order.get_json()
    assert order.get_json()["data"]["status"] == "DELIVERED"
    assert order.get_json()["data"]["delivered_at"]

    notes = client.get("/api/v1/notifications", headers=owner)
    assert notes.status_code == 200, notes.get_json()
    types = {row["type"] for row in notes.get_json()["data"]}
    assert "DELIVERY_OUT_FOR_DELIVERY" in types
    assert "DELIVERY_COMPLETED" in types


def test_installation_from_furniture_custom_order(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_furniture(client, owner)
    oid = _create_ready_order(client, billing, title="Modular Kitchen")

    scheduled = (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%dT11:00:00")
    created = client.post(
        "/api/v1/furniture/installations",
        headers=owner,
        json={
            "custom_order_id": oid,
            "scheduled_at": scheduled,
            "install_address": "Flat 4, Lake View Apartments",
            "technician_name": "Suresh",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["installation_number"].startswith("INS-")
    assert body["custom_order_id"] == oid
    assert body["custom_order_title"] == "Modular Kitchen"
    assert body["serial_unit_id"] is None
    assert body["status"] == "SCHEDULED"

    completed = client.patch(
        f"/api/v1/installations/{body['id']}/status",
        headers=owner,
        json={"status": "IN_PROGRESS"},
    )
    assert completed.status_code == 200, completed.get_json()
    finished = client.patch(
        f"/api/v1/installations/{body['id']}/status",
        headers=owner,
        json={"status": "COMPLETED"},
    )
    assert finished.status_code == 200, finished.get_json()
    assert finished.get_json()["data"]["status"] == "COMPLETED"


def test_delivery_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_furniture(client, owner_a)
    oid = _create_ready_order(client, billing)

    created = client.post(
        "/api/v1/deliveries",
        headers=owner_a,
        json={
            "custom_order_id": oid,
            "delivery_address": "Tenant A address",
        },
    )
    assert created.status_code == 201, created.get_json()
    did = created.get_json()["data"]["id"]

    _switch_furniture(client, owner_b)
    foreign = client.get(f"/api/v1/deliveries/{did}", headers=owner_b)
    assert foreign.status_code == 404, foreign.get_json()
