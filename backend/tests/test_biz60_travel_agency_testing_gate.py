"""Sprint BIZ-60 — travel agency testing gate.

Regression matrix across BIZ-56 … BIZ-59: tour packages, bookings/payments,
itinerary + document metadata (PII isolation), agents/commission, module
matrix, permissions, audit, notifications, and API contracts.

Run full phase gate from backend/:
  python -m pytest tests/test_biz56_tour_packages.py \\
    tests/test_biz57_travel_bookings.py \\
    tests/test_biz58_travel_itinerary_documents.py \\
    tests/test_biz59_travel_agent_commission.py \\
    tests/test_biz60_travel_agency_testing_gate.py -q
"""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type: str):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_restaurant_travel_vertical_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    for path in (
        "/api/v1/tour-packages",
        "/api/v1/travel/packages",
        "/api/v1/travel-bookings",
        "/api/v1/travel/bookings",
        "/api/v1/travel-agents",
        "/api/v1/travel/agents",
        "/api/v1/commissions",
        "/api/v1/commissions/report",
        "/api/v1/travel/commissions",
        "/api/v1/travel/commissions/report",
    ):
        assert client.get(path, headers=owner).status_code == 403, path


def test_gate_module_matrix_travel(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in (
        "tour_packages",
        "travel_bookings",
        "travel_commission",
        "custom_orders",
    ):
        assert code in modules, code
    for code in (
        "serial_imei",
        "warehouse",
        "price_lists",
        "production",
        "order_channels",
        "book_metadata",
        "furniture_attributes",
    ):
        assert code not in modules, code


def test_gate_package_booking_itinerary_docs_commission_flow(client):
    """Happy path tying BIZ-56…59 together with PII document + commission."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "travel_agency")

    pkg = client.post(
        "/api/v1/travel/packages",
        headers=owner,
        json={
            "code": "GATE-GOA",
            "name": "Gate Goa Escape",
            "destination": "Goa",
            "duration_days": 3,
            "base_price": "12000",
            "gst_percentage": "0",
        },
    )
    assert pkg.status_code == 201, pkg.get_json()
    package = pkg.get_json()["data"]
    assert package["stock_tracked"] is False
    assert "CREATE_TOUR_PACKAGE" in _audit_actions(client, owner, action="CREATE_TOUR_PACKAGE")

    bill = client.post(
        f"/api/v1/travel/packages/{package['id']}/bill",
        headers=billing,
        json={"quantity": 1, "payment_method": "cash"},
    )
    assert bill.status_code == 201, bill.get_json()
    item = client.get(f"/api/v1/items/{package['item_id']}", headers=owner).get_json()["data"]
    assert item["stock_quantity"] is None

    agent = client.post(
        "/api/v1/travel/agents",
        headers=owner,
        json={"code": "GATE-AG", "name": "Gate Agent", "commission_percent": "10"},
    )
    assert agent.status_code == 201, agent.get_json()
    agent_id = agent.get_json()["data"]["id"]
    assert "CREATE_TRAVEL_AGENT" in _audit_actions(client, owner, action="CREATE_TRAVEL_AGENT")

    booking = client.post(
        "/api/v1/travel/bookings",
        headers=billing,
        json={
            "package_id": package["id"],
            "customer_name": "Gate Traveler",
            "pax_count": 2,
            "advance_amount": "5000",
            "payment_method": "cash",
            "agent_id": agent_id,
        },
    )
    assert booking.status_code == 201, booking.get_json()
    body = booking.get_json()["data"]
    bid = body["id"]
    assert body["booking_number"].startswith("TB-")
    assert Decimal(str(body["total_amount"])) == Decimal("24000")
    assert Decimal(str(body["remaining_amount"])) == Decimal("19000")
    assert body["commission"] is not None
    assert Decimal(str(body["commission"]["commission_amount"])) == Decimal("2400")
    assert "CREATE_TRAVEL_BOOKING" in _audit_actions(client, owner, action="CREATE_TRAVEL_BOOKING")
    assert "CREATE_TRAVEL_COMMISSION" in _audit_actions(
        client, owner, action="CREATE_TRAVEL_COMMISSION"
    )

    notes = client.get("/api/v1/notifications", headers=owner, query_string={"per_page": 50})
    assert any(n["type"] == "TRAVEL_PAYMENT_DUE" for n in notes.get_json()["data"])

    hotel = client.post(
        f"/api/v1/travel/bookings/{bid}/itinerary",
        headers=manager,
        json={
            "item_type": "HOTEL",
            "day_number": 1,
            "title": "Gate Resort",
            "confirmation_ref": "HTL-GATE",
        },
    )
    assert hotel.status_code == 201, hotel.get_json()
    assert "CREATE_TRAVEL_ITINERARY_ITEM" in _audit_actions(
        client, owner, action="CREATE_TRAVEL_ITINERARY_ITEM"
    )

    vehicle = client.post(
        f"/api/v1/travel-bookings/{bid}/itinerary",
        headers=owner,
        json={"item_type": "VEHICLE", "title": "Airport cab", "confirmation_ref": "CAB-1"},
    )
    assert vehicle.status_code == 201, vehicle.get_json()

    doc = client.post(
        f"/api/v1/travel/bookings/{bid}/documents",
        headers=owner,
        json={
            "document_type": "PASSPORT",
            "holder_name": "Gate Traveler",
            "document_number": "Z9999988",
            "issued_country": "IN",
            "expiry_date": "2031-06-01",
            "file_name": "passport-gate.pdf",
        },
    )
    assert doc.status_code == 201, doc.get_json()
    doc_id = doc.get_json()["data"]["id"]
    assert "CREATE_TRAVEL_BOOKING_DOCUMENT" in _audit_actions(
        client, owner, action="CREATE_TRAVEL_BOOKING_DOCUMENT"
    )

    detail = client.get(f"/api/v1/travel/bookings/{bid}", headers=billing).get_json()["data"]
    assert detail["itinerary_count"] == 2
    assert detail["document_count"] == 1

    confirmed = client.patch(
        f"/api/v1/travel/bookings/{bid}/status",
        headers=manager,
        json={"status": "CONFIRMED"},
    )
    assert confirmed.status_code == 200, confirmed.get_json()
    notes2 = client.get("/api/v1/notifications", headers=owner, query_string={"per_page": 50})
    assert any(n["type"] == "TRAVEL_BOOKING_CONFIRMED" for n in notes2.get_json()["data"])

    paid = client.post(
        f"/api/v1/travel/bookings/{bid}/payments",
        headers=billing,
        json={"amount": "19000", "payment_method": "online"},
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

    report = client.get("/api/v1/commissions/report", headers=owner)
    assert report.status_code == 200, report.get_json()
    row = next(r for r in report.get_json()["data"] if r["agent_id"] == agent_id)
    assert Decimal(str(row["commission_total"])) == Decimal("2400")
    assert Decimal(str(row["pending_total"])) == Decimal("2400")

    entries = client.get(
        "/api/v1/travel/commissions",
        headers=owner,
        query_string={"agent_id": agent_id},
    ).get_json()["data"]
    entry_id = entries[0]["id"]
    marked = client.patch(
        f"/api/v1/commissions/{entry_id}/status",
        headers=owner,
        json={"status": "PAID"},
    )
    assert marked.status_code == 200, marked.get_json()
    assert "UPDATE_TRAVEL_COMMISSION_STATUS" in _audit_actions(
        client, owner, action="UPDATE_TRAVEL_COMMISSION_STATUS"
    )

    deleted = client.delete(
        f"/api/v1/travel/bookings/{bid}/documents/{doc_id}",
        headers=owner,
    )
    assert deleted.status_code == 200
    assert "DELETE_TRAVEL_BOOKING_DOCUMENT" in _audit_actions(
        client, owner, action="DELETE_TRAVEL_BOOKING_DOCUMENT"
    )
    assert (
        client.get(f"/api/v1/travel/bookings/{bid}/documents", headers=owner).get_json()["data"]
        == []
    )


def test_gate_document_pii_cross_tenant_isolation(client):
    """Document metadata must never leak across tenants."""
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "travel_agency")
    _switch(client, owner_b, "travel_agency")

    pkg = client.post(
        "/api/v1/tour-packages",
        headers=owner_a,
        json={
            "code": "ISO-DOC",
            "name": "Iso Doc Trip",
            "destination": "Manali",
            "duration_days": 2,
            "base_price": "8000",
            "gst_percentage": "0",
        },
    ).get_json()["data"]
    booking = client.post(
        "/api/v1/travel/bookings",
        headers=owner_a,
        json={"package_id": pkg["id"], "customer_name": "Private Pax"},
    ).get_json()["data"]
    bid = booking["id"]

    doc = client.post(
        f"/api/v1/travel/bookings/{bid}/documents",
        headers=owner_a,
        json={
            "document_type": "PASSPORT",
            "holder_name": "Secret Holder",
            "document_number": "SECRET99",
            "file_name": "secret.pdf",
        },
    ).get_json()["data"]
    item = client.post(
        f"/api/v1/travel/bookings/{bid}/itinerary",
        headers=owner_a,
        json={"item_type": "TICKET", "title": "Private Flight"},
    ).get_json()["data"]

    assert client.get(f"/api/v1/travel/bookings/{bid}", headers=owner_b).status_code == 404
    assert client.get(f"/api/v1/travel/bookings/{bid}/documents", headers=owner_b).status_code == 404
    assert (
        client.delete(
            f"/api/v1/travel/bookings/{bid}/documents/{doc['id']}",
            headers=owner_b,
        ).status_code
        == 404
    )
    assert client.get(f"/api/v1/travel/bookings/{bid}/itinerary", headers=owner_b).status_code == 404
    assert (
        client.delete(
            f"/api/v1/travel/bookings/{bid}/itinerary/{item['id']}",
            headers=owner_b,
        ).status_code
        == 404
    )


def test_gate_billing_permissions(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "travel_agency")

    assert (
        client.post(
            "/api/v1/travel/packages",
            headers=billing,
            json={
                "code": "BLOCK",
                "name": "Blocked",
                "destination": "X",
                "duration_days": 1,
                "base_price": "100",
                "gst_percentage": "0",
            },
        ).status_code
        == 403
    )
    assert client.get("/api/v1/travel/packages", headers=billing).status_code == 200

    pkg = client.post(
        "/api/v1/travel/packages",
        headers=owner,
        json={
            "code": "PERM1",
            "name": "Perm Package",
            "destination": "Pune",
            "duration_days": 1,
            "base_price": "5000",
            "gst_percentage": "0",
        },
    ).get_json()["data"]

    assert (
        client.post(
            "/api/v1/travel/agents",
            headers=billing,
            json={"code": "B", "name": "Blocked", "commission_percent": "5"},
        ).status_code
        == 403
    )
    assert client.get("/api/v1/travel/agents", headers=billing).status_code == 200

    booking = client.post(
        "/api/v1/travel/bookings",
        headers=billing,
        json={"package_id": pkg["id"], "customer_name": "Perm"},
    )
    assert booking.status_code == 201, booking.get_json()
    bid = booking.get_json()["data"]["id"]

    assert (
        client.patch(
            f"/api/v1/travel/bookings/{bid}/status",
            headers=billing,
            json={"status": "CONFIRMED"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/travel/bookings/{bid}/itinerary",
            headers=billing,
            json={"title": "Nope"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/travel/bookings/{bid}/documents",
            headers=billing,
            json={"document_type": "ID", "document_number": "X"},
        ).status_code
        == 403
    )
    assert client.get(f"/api/v1/travel/bookings/{bid}/itinerary", headers=billing).status_code == 200
    assert client.get(f"/api/v1/travel/bookings/{bid}/documents", headers=billing).status_code == 200
    assert client.get("/api/v1/commissions/report", headers=billing).status_code == 200


def test_gate_api_envelopes(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    for path in (
        "/api/v1/tour-packages",
        "/api/v1/travel/packages",
        "/api/v1/travel-bookings",
        "/api/v1/travel/bookings",
        "/api/v1/travel-agents",
        "/api/v1/travel/agents",
        "/api/v1/commissions",
        "/api/v1/commissions/report",
        "/api/v1/travel/commissions",
        "/api/v1/travel/commissions/report",
    ):
        response = client.get(path, headers=owner)
        assert response.status_code == 200, path
        body = response.get_json()
        assert body["success"] is True, path
        assert "data" in body, path


def test_gate_cannot_complete_with_balance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    pkg = client.post(
        "/api/v1/travel/packages",
        headers=owner,
        json={
            "code": "BAL1",
            "name": "Balance Trip",
            "destination": "Goa",
            "duration_days": 2,
            "base_price": "4000",
            "gst_percentage": "0",
        },
    ).get_json()["data"]
    bid = client.post(
        "/api/v1/travel/bookings",
        headers=owner,
        json={"package_id": pkg["id"], "advance_amount": "500"},
    ).get_json()["data"]["id"]
    for status in ("CONFIRMED", "IN_PROGRESS"):
        assert (
            client.patch(
                f"/api/v1/travel/bookings/{bid}/status",
                headers=owner,
                json={"status": status},
            ).status_code
            == 200
        )
    blocked = client.patch(
        f"/api/v1/travel/bookings/{bid}/status",
        headers=owner,
        json={"status": "COMPLETED"},
    )
    assert blocked.status_code == 400, blocked.get_json()
    assert "outstanding" in blocked.get_json()["error"]["message"].lower()
