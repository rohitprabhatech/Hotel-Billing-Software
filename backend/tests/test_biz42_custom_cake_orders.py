"""Sprint BIZ-42 — custom cake orders and advance payments."""

from datetime import datetime, timedelta

from tests.conftest import login


def _switch(client, headers, business_type="bakery_sweet"):
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


def test_create_cake_order_advance_less_than_total(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)

    denied_full = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={
            "order_type": "bakery",
            "title": "Full pay cake",
            "total_amount": "1000",
            "advance_amount": "1000",
        },
    )
    assert denied_full.status_code == 400, denied_full.get_json()

    delivery = (datetime.utcnow() + timedelta(days=2)).isoformat()
    created = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={
            "order_type": "bakery",
            "title": "Chocolate Truffle",
            "size": "2 kg",
            "flavor": "Chocolate",
            "customer_name": "Anita",
            "customer_phone": "9000000042",
            "total_amount": "2500",
            "advance_amount": "500",
            "payment_method": "upi",
            "delivery_at": delivery,
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["order_number"].startswith("CO-")
    assert body["status"] == "BOOKED"
    assert body["advance_paid"] == 500.0
    assert body["remaining_amount"] == 2000.0
    assert len(body["payments"]) == 1

    alias = client.get("/api/v1/bakery/cake-orders", headers=owner)
    assert alias.status_code == 200, alias.get_json()
    assert any(row["id"] == body["id"] for row in alias.get_json()["data"])


def test_status_pipeline_and_billing_cannot_manage(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner)

    created = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={
            "title": "Red Velvet",
            "size": "1 kg",
            "flavor": "Red velvet",
            "total_amount": "1800",
            "advance_amount": "300",
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

    for status in ("CONFIRMED", "IN_PRODUCTION", "READY", "DELIVERED"):
        updated = client.patch(
            f"/api/v1/custom-orders/{oid}/status",
            headers=manager if status != "DELIVERED" else owner,
            json={"status": status},
        )
        assert updated.status_code == 200, updated.get_json()
        assert updated.get_json()["data"]["status"] == status

    assert updated.get_json()["data"]["delivered_at"]


def test_record_additional_advance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    created = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={"title": "Fruit Cake", "total_amount": "1200", "advance_amount": "200"},
    )
    oid = created.get_json()["data"]["id"]

    over = client.post(
        f"/api/v1/custom-orders/{oid}/advance",
        headers=billing,
        json={"amount": "1100"},
    )
    assert over.status_code == 400, over.get_json()

    paid = client.post(
        f"/api/v1/custom-orders/{oid}/advance",
        headers=billing,
        json={"amount": "400", "payment_method": "cash"},
    )
    assert paid.status_code == 201, paid.get_json()
    body = paid.get_json()["data"]
    assert body["advance_paid"] == 600.0
    assert body["remaining_amount"] == 600.0
    assert len(body["payments"]) == 2


def test_custom_order_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a)
    _switch(client, owner_b)
    created = client.post(
        "/api/v1/custom-orders",
        headers=owner_a,
        json={"title": "Iso Cake", "total_amount": "900", "advance_amount": "100"},
    )
    assert created.status_code == 201, created.get_json()
    oid = created.get_json()["data"]["id"]

    foreign = client.get(f"/api/v1/custom-orders/{oid}", headers=owner_b)
    assert foreign.status_code == 404, foreign.get_json()
