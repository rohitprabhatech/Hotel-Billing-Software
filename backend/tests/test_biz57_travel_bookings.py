"""Sprint BIZ-57 — travel bookings, advances, and status pipeline."""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _package(client, headers, code="GOA3N", name="Goa Escape", price="10000"):
    response = client.post(
        "/api/v1/travel/packages",
        headers=headers,
        json={
            "code": code,
            "name": name,
            "destination": "Goa",
            "duration_days": 4,
            "base_price": price,
            "gst_percentage": "0",
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_restaurant_bookings_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/travel-bookings", headers=owner).status_code == 403
    assert client.get("/api/v1/travel/bookings", headers=owner).status_code == 403


def test_booking_advance_remaining_and_complete(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "travel_agency")
    pkg = _package(client, owner)

    created = client.post(
        "/api/v1/travel/bookings",
        headers=billing,
        json={
            "package_id": pkg["id"],
            "customer_name": "Anita",
            "pax_count": 2,
            "advance_amount": "4000",
            "payment_method": "cash",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["booking_number"].startswith("TB-")
    assert body["status"] == "BOOKED"
    assert Decimal(str(body["total_amount"])) == Decimal("20000")  # 10000 × 2
    assert Decimal(str(body["advance_paid"])) == Decimal("4000")
    assert Decimal(str(body["remaining_amount"])) == Decimal("16000")
    bid = body["id"]

    notes = client.get("/api/v1/notifications", headers=owner, query_string={"per_page": 50})
    assert any(n["type"] == "TRAVEL_PAYMENT_DUE" for n in notes.get_json()["data"])

    denied = client.patch(
        f"/api/v1/travel/bookings/{bid}/status",
        headers=billing,
        json={"status": "CONFIRMED"},
    )
    assert denied.status_code == 403, denied.get_json()

    confirmed = client.patch(
        f"/api/v1/travel/bookings/{bid}/status",
        headers=manager,
        json={"status": "CONFIRMED"},
    )
    assert confirmed.status_code == 200, confirmed.get_json()
    assert confirmed.get_json()["data"]["status"] == "CONFIRMED"

    notes2 = client.get("/api/v1/notifications", headers=owner, query_string={"per_page": 50})
    assert any(n["type"] == "TRAVEL_BOOKING_CONFIRMED" for n in notes2.get_json()["data"])

    paid = client.post(
        f"/api/v1/travel/bookings/{bid}/payments",
        headers=billing,
        json={"amount": "16000", "payment_method": "online"},
    )
    assert paid.status_code == 201, paid.get_json()
    assert Decimal(str(paid.get_json()["data"]["remaining_amount"])) == Decimal("0")

    client.patch(
        f"/api/v1/travel-bookings/{bid}/status",
        headers=owner,
        json={"status": "IN_PROGRESS"},
    )
    completed = client.patch(
        f"/api/v1/travel-bookings/{bid}/status",
        headers=owner,
        json={"status": "COMPLETED"},
    )
    assert completed.status_code == 200, completed.get_json()
    assert completed.get_json()["data"]["status"] == "COMPLETED"
    assert completed.get_json()["data"]["completed_at"]


def test_cannot_complete_with_outstanding_balance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    pkg = _package(client, owner, code="KER2N", name="Kerala", price="5000")

    created = client.post(
        "/api/v1/travel-bookings",
        headers=owner,
        json={
            "package_id": pkg["id"],
            "customer_name": "Ravi",
            "advance_amount": "1000",
        },
    )
    bid = created.get_json()["data"]["id"]
    client.patch(
        f"/api/v1/travel-bookings/{bid}/status",
        headers=owner,
        json={"status": "CONFIRMED"},
    )
    client.patch(
        f"/api/v1/travel-bookings/{bid}/status",
        headers=owner,
        json={"status": "IN_PROGRESS"},
    )
    blocked = client.patch(
        f"/api/v1/travel-bookings/{bid}/status",
        headers=owner,
        json={"status": "COMPLETED"},
    )
    assert blocked.status_code == 400, blocked.get_json()
    assert "outstanding" in blocked.get_json()["error"]["message"].lower()


def test_booking_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "travel_agency")
    _switch(client, owner_b, "travel_agency")
    pkg = _package(client, owner_a, code="ISO1", name="Iso Trip")
    created = client.post(
        "/api/v1/travel/bookings",
        headers=owner_a,
        json={"package_id": pkg["id"], "customer_name": "Iso"},
    )
    bid = created.get_json()["data"]["id"]
    assert client.get(f"/api/v1/travel/bookings/{bid}", headers=owner_b).status_code == 404
