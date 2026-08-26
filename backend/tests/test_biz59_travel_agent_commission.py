"""Sprint BIZ-59 — travel agents and commission on bookings."""

from decimal import Decimal

from app.services.travel_agent_service import TravelAgentService
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


def test_commission_math_helper():
    assert TravelAgentService.calc_commission("20000", "10") == Decimal("2000.00")
    assert TravelAgentService.calc_commission("999.99", "7.5") == Decimal("75.00")


def test_agent_booking_commission_and_report(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "travel_agency")
    pkg = _package(client, owner)

    denied = client.post(
        "/api/v1/travel/agents",
        headers=billing,
        json={"code": "AG1", "name": "Rina", "commission_percent": "10"},
    )
    assert denied.status_code == 403, denied.get_json()

    agent = client.post(
        "/api/v1/travel-agents",
        headers=owner,
        json={"code": "AG1", "name": "Rina", "commission_percent": "10"},
    )
    assert agent.status_code == 201, agent.get_json()
    agent_id = agent.get_json()["data"]["id"]
    assert float(agent.get_json()["data"]["commission_percent"]) == 10.0

    booking = client.post(
        "/api/v1/travel/bookings",
        headers=owner,
        json={
            "package_id": pkg["id"],
            "customer_name": "Anita",
            "pax_count": 2,
            "agent_id": agent_id,
        },
    )
    assert booking.status_code == 201, booking.get_json()
    body = booking.get_json()["data"]
    assert body["agent_id"] == agent_id
    assert body["commission"] is not None
    # 10000 × 2 pax = 20000; 10% = 2000
    assert Decimal(str(body["total_amount"])) == Decimal("20000")
    assert Decimal(str(body["commission"]["commission_amount"])) == Decimal("2000")
    assert body["commission"]["status"] == "PENDING"
    bid = body["id"]

    entries = client.get("/api/v1/commissions", headers=owner)
    assert entries.status_code == 200
    assert len(entries.get_json()["data"]) == 1
    entry_id = entries.get_json()["data"][0]["id"]

    report = client.get("/api/v1/travel/commissions/report", headers=billing)
    assert report.status_code == 200
    rows = report.get_json()["data"]
    assert len(rows) == 1
    assert rows[0]["agent_id"] == agent_id
    assert Decimal(str(rows[0]["commission_total"])) == Decimal("2000")
    assert Decimal(str(rows[0]["pending_total"])) == Decimal("2000")
    assert Decimal(str(rows[0]["paid_total"])) == Decimal("0")

    paid = client.patch(
        f"/api/v1/commissions/{entry_id}/status",
        headers=owner,
        json={"status": "PAID"},
    )
    assert paid.status_code == 200, paid.get_json()
    assert paid.get_json()["data"]["status"] == "PAID"
    assert paid.get_json()["data"]["paid_at"]

    report2 = client.get("/api/v1/commissions/report", headers=owner)
    assert Decimal(str(report2.get_json()["data"][0]["paid_total"])) == Decimal("2000")
    assert Decimal(str(report2.get_json()["data"][0]["pending_total"])) == Decimal("0")

    # Assign commission later with override percent
    booking2 = client.post(
        "/api/v1/travel/bookings",
        headers=owner,
        json={"package_id": pkg["id"], "customer_name": "NoAgent", "pax_count": 1},
    )
    bid2 = booking2.get_json()["data"]["id"]
    created = client.post(
        "/api/v1/travel/commissions",
        headers=owner,
        json={"booking_id": bid2, "agent_id": agent_id, "commission_percent": "5"},
    )
    assert created.status_code == 201, created.get_json()
    assert Decimal(str(created.get_json()["data"]["commission_amount"])) == Decimal("500.00")
    assert Decimal(str(created.get_json()["data"]["commission_percent"])) == Decimal("5")

    # Booking without agent still works
    assert bid and bid2


def test_commission_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "travel_agency")
    _switch(client, owner_b, "travel_agency")
    agent = client.post(
        "/api/v1/travel/agents",
        headers=owner_a,
        json={"code": "ISO", "name": "Iso Agent", "commission_percent": "8"},
    )
    agent_id = agent.get_json()["data"]["id"]
    assert client.get(f"/api/v1/travel/agents/{agent_id}", headers=owner_b).status_code == 404
    assert client.get("/api/v1/commissions/report", headers=owner_b).get_json()["data"] == []


def test_restaurant_commission_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/travel-agents", headers=owner).status_code == 403
    assert client.get("/api/v1/commissions", headers=owner).status_code == 403
