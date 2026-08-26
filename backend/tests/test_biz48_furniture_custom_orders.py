"""Sprint BIZ-48 — furniture custom orders and advance payments."""

from datetime import datetime, timedelta

from tests.conftest import login


def _switch(client, headers, business_type="furniture"):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def test_restaurant_custom_orders_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/custom-orders", headers=owner).status_code == 403
    assert client.get("/api/v1/furniture/custom-orders", headers=owner).status_code == 403


def test_create_furniture_order_advance_less_than_total(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)

    denied_full = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={
            "order_type": "furniture",
            "title": "Full pay sofa",
            "total_amount": "10000",
            "advance_amount": "10000",
        },
    )
    assert denied_full.status_code == 400, denied_full.get_json()

    delivery = (datetime.utcnow() + timedelta(days=7)).isoformat()
    created = client.post(
        "/api/v1/furniture/custom-orders",
        headers=billing,
        json={
            "title": "Teak Sofa Set",
            "size": "84×36×32",
            "flavor": "Teak",
            "customer_name": "Ravi",
            "customer_phone": "9000000048",
            "total_amount": "45000",
            "advance_amount": "15000",
            "payment_method": "upi",
            "delivery_at": delivery,
            "notes": "Walnut polish",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["order_type"] == "furniture"
    assert body["order_number"].startswith("CO-")
    assert body["status"] == "BOOKED"
    assert body["advance_paid"] == 15000.0
    assert body["remaining_amount"] == 30000.0
    assert body["size"] == "84×36×32"
    assert body["flavor"] == "Teak"
    assert len(body["payments"]) == 1

    alias = client.get("/api/v1/furniture/custom-orders", headers=owner)
    assert alias.status_code == 200, alias.get_json()
    assert any(row["id"] == body["id"] for row in alias.get_json()["data"])

    bakery_only = client.get(
        "/api/v1/custom-orders",
        headers=owner,
        query_string={"order_type": "bakery"},
    )
    assert bakery_only.status_code == 200
    assert all(row["id"] != body["id"] for row in bakery_only.get_json()["data"])


def test_furniture_status_pipeline_and_billing_cannot_manage(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner)

    created = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={
            "order_type": "furniture",
            "title": "Dining Table",
            "size": "180×90×75",
            "flavor": "Rosewood",
            "total_amount": "28000",
            "advance_amount": "8000",
        },
    )
    assert created.status_code == 201, created.get_json()
    oid = created.get_json()["data"]["id"]

    denied = client.patch(
        f"/api/v1/custom-orders/{oid}/status",
        headers=billing,
        json={"status": "CONFIRMED"},
    )
    assert denied.status_code == 403, denied.get_json()

    for status in ("CONFIRMED", "IN_PRODUCTION", "READY"):
        updated = client.patch(
            f"/api/v1/custom-orders/{oid}/status",
            headers=manager if status != "DELIVERED" else owner,
            json={"status": status},
        )
        assert updated.status_code == 200, updated.get_json()
        assert updated.get_json()["data"]["status"] == status

    blocked = client.patch(
        f"/api/v1/custom-orders/{oid}/status",
        headers=owner,
        json={"status": "DELIVERED"},
    )
    assert blocked.status_code == 400, blocked.get_json()

    delivery = client.post(
        "/api/v1/furniture/deliveries",
        headers=owner,
        json={
            "custom_order_id": oid,
            "delivery_address": "Showroom delivery lane",
        },
    )
    assert delivery.status_code == 201, delivery.get_json()
    did = delivery.get_json()["data"]["id"]

    for status in ("OUT_FOR_DELIVERY", "DELIVERED"):
        updated = client.patch(
            f"/api/v1/deliveries/{did}/status",
            headers=owner,
            json={"status": status},
        )
        assert updated.status_code == 200, updated.get_json()

    final = client.get(f"/api/v1/custom-orders/{oid}", headers=owner)
    assert final.status_code == 200, final.get_json()
    assert final.get_json()["data"]["status"] == "DELIVERED"
    assert final.get_json()["data"]["delivered_at"]


def test_furniture_record_additional_advance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    created = client.post(
        "/api/v1/furniture/custom-orders",
        headers=billing,
        json={"title": "Wardrobe", "total_amount": "22000", "advance_amount": "5000"},
    )
    oid = created.get_json()["data"]["id"]

    over = client.post(
        f"/api/v1/furniture/custom-orders/{oid}/advance",
        headers=billing,
        json={"amount": "20000"},
    )
    assert over.status_code == 400, over.get_json()

    paid = client.post(
        f"/api/v1/furniture/custom-orders/{oid}/advance",
        headers=billing,
        json={"amount": "7000", "payment_method": "cash"},
    )
    assert paid.status_code == 201, paid.get_json()
    body = paid.get_json()["data"]
    assert body["advance_paid"] == 12000.0
    assert body["remaining_amount"] == 10000.0
    assert len(body["payments"]) == 2


def test_furniture_order_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a)
    _switch(client, owner_b)
    created = client.post(
        "/api/v1/custom-orders",
        headers=owner_a,
        json={
            "order_type": "furniture",
            "title": "Iso Bed",
            "total_amount": "15000",
            "advance_amount": "2000",
        },
    )
    assert created.status_code == 201, created.get_json()
    oid = created.get_json()["data"]["id"]

    foreign = client.get(f"/api/v1/custom-orders/{oid}", headers=owner_b)
    assert foreign.status_code == 404, foreign.get_json()
