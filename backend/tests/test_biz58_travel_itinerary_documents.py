"""Sprint BIZ-58 — travel itinerary + document metadata on bookings."""

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


def _booking(client, headers, package_id):
    response = client.post(
        "/api/v1/travel/bookings",
        headers=headers,
        json={"package_id": package_id, "customer_name": "Meera", "pax_count": 2},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_itinerary_and_documents_crud(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "travel_agency")
    pkg = _package(client, owner)
    booking = _booking(client, owner, pkg["id"])
    bid = booking["id"]

    denied = client.post(
        f"/api/v1/travel/bookings/{bid}/itinerary",
        headers=billing,
        json={"item_type": "HOTEL", "title": "Beach Resort"},
    )
    assert denied.status_code == 403, denied.get_json()

    hotel = client.post(
        f"/api/v1/travel/bookings/{bid}/itinerary",
        headers=owner,
        json={
            "item_type": "HOTEL",
            "day_number": 1,
            "title": "Beach Resort",
            "location": "Calangute",
            "vendor_name": "Taj",
            "confirmation_ref": "HTL-1",
        },
    )
    assert hotel.status_code == 201, hotel.get_json()
    item_id = hotel.get_json()["data"]["id"]
    assert hotel.get_json()["data"]["item_type"] == "HOTEL"

    vehicle = client.post(
        f"/api/v1/travel-bookings/{bid}/itinerary",
        headers=owner,
        json={
            "item_type": "VEHICLE",
            "day_number": 1,
            "title": "Airport transfer",
            "vendor_name": "Goa Cabs",
            "confirmation_ref": "CAB-9",
        },
    )
    assert vehicle.status_code == 201, vehicle.get_json()

    ticket = client.post(
        f"/api/v1/travel/bookings/{bid}/itinerary",
        headers=owner,
        json={
            "item_type": "TICKET",
            "day_number": 2,
            "title": "Ferry to Divar",
            "confirmation_ref": "TKT-22",
        },
    )
    assert ticket.status_code == 201, ticket.get_json()

    patched = client.patch(
        f"/api/v1/travel/bookings/{bid}/itinerary/{item_id}",
        headers=owner,
        json={"confirmation_ref": "HTL-1A", "notes": "Sea view"},
    )
    assert patched.status_code == 200, patched.get_json()
    assert patched.get_json()["data"]["confirmation_ref"] == "HTL-1A"
    assert patched.get_json()["data"]["item_type"] == "HOTEL"

    listed = client.get(f"/api/v1/travel/bookings/{bid}/itinerary", headers=billing)
    assert listed.status_code == 200
    assert len(listed.get_json()["data"]) == 3

    doc = client.post(
        f"/api/v1/travel/bookings/{bid}/documents",
        headers=owner,
        json={
            "document_type": "PASSPORT",
            "holder_name": "Meera Shah",
            "document_number": "Z1234567",
            "issued_country": "IN",
            "expiry_date": "2030-01-15",
            "file_name": "passport-meera.pdf",
        },
    )
    assert doc.status_code == 201, doc.get_json()
    doc_id = doc.get_json()["data"]["id"]
    assert doc.get_json()["data"]["document_type"] == "PASSPORT"

    docs = client.get(f"/api/v1/travel-bookings/{bid}/documents", headers=owner)
    assert docs.status_code == 200
    assert len(docs.get_json()["data"]) == 1

    detail = client.get(f"/api/v1/travel/bookings/{bid}", headers=owner)
    assert detail.status_code == 200
    body = detail.get_json()["data"]
    assert body["itinerary_count"] == 3
    assert body["document_count"] == 1

    deleted_doc = client.delete(
        f"/api/v1/travel/bookings/{bid}/documents/{doc_id}",
        headers=owner,
    )
    assert deleted_doc.status_code == 200
    assert (
        client.get(f"/api/v1/travel/bookings/{bid}/documents", headers=owner)
        .get_json()["data"]
        == []
    )

    deleted_item = client.delete(
        f"/api/v1/travel/bookings/{bid}/itinerary/{item_id}",
        headers=owner,
    )
    assert deleted_item.status_code == 200
    assert len(client.get(f"/api/v1/travel/bookings/{bid}/itinerary", headers=owner).get_json()["data"]) == 2


def test_detail_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "travel_agency")
    _switch(client, owner_b, "travel_agency")
    pkg = _package(client, owner_a, code="ISO58", name="Iso 58")
    booking = _booking(client, owner_a, pkg["id"])
    bid = booking["id"]

    item = client.post(
        f"/api/v1/travel/bookings/{bid}/itinerary",
        headers=owner_a,
        json={"item_type": "ACTIVITY", "title": "Private"},
    )
    item_id = item.get_json()["data"]["id"]
    doc = client.post(
        f"/api/v1/travel/bookings/{bid}/documents",
        headers=owner_a,
        json={"document_type": "ID", "document_number": "A1"},
    )
    doc_id = doc.get_json()["data"]["id"]

    assert client.get(f"/api/v1/travel/bookings/{bid}/itinerary", headers=owner_b).status_code == 404
    assert (
        client.post(
            f"/api/v1/travel/bookings/{bid}/itinerary",
            headers=owner_b,
            json={"title": "Hack"},
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/travel/bookings/{bid}/itinerary/{item_id}",
            headers=owner_b,
            json={"title": "Hack"},
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/api/v1/travel/bookings/{bid}/itinerary/{item_id}",
            headers=owner_b,
        ).status_code
        == 404
    )
    assert client.get(f"/api/v1/travel/bookings/{bid}/documents", headers=owner_b).status_code == 404
    assert (
        client.delete(
            f"/api/v1/travel/bookings/{bid}/documents/{doc_id}",
            headers=owner_b,
        ).status_code
        == 404
    )


def test_restaurant_travel_details_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/travel/bookings/x/itinerary", headers=owner).status_code == 403
    assert client.get("/api/v1/travel/bookings/x/documents", headers=owner).status_code == 403
