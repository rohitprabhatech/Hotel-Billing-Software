"""Sprint BIZ-56 — travel tour package management (service billing, no stock)."""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def test_restaurant_tour_packages_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/tour-packages", headers=owner).status_code == 403
    assert client.get("/api/v1/travel/packages", headers=owner).status_code == 403


def test_travel_module_has_tour_packages(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    assert "tour_packages" in modules
    assert "warehouse" not in modules


def test_create_package_and_bill_without_stock(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "travel_agency")

    created = client.post(
        "/api/v1/travel/packages",
        headers=owner,
        json={
            "code": "GOA3N",
            "name": "Goa 3N/4D",
            "destination": "Goa",
            "duration_days": 4,
            "base_price": "14999",
            "gst_percentage": "5",
            "description": "Beach package",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["code"] == "GOA3N"
    assert body["stock_tracked"] is False
    assert body["item_id"]
    package_id = body["id"]
    item_id = body["item_id"]

    item = client.get(f"/api/v1/items/{item_id}", headers=owner)
    assert item.status_code == 200, item.get_json()
    assert item.get_json()["data"]["stock_quantity"] is None

    # Direct bill via linked item
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item_id, "quantity": "1"}],
            "payment_method": "cash",
            "customer_name": "Traveler",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    data = bill.get_json()["data"]
    assert Decimal(str(data["taxable_amount"])) == Decimal("14999.00")
    assert Decimal(str(data["gst_amount"])) > 0

    # Stock still untracked; no deduction possible
    item_after = client.get(f"/api/v1/items/{item_id}", headers=owner).get_json()["data"]
    assert item_after["stock_quantity"] is None

    # Service bill helper
    billed = client.post(
        f"/api/v1/travel/packages/{package_id}/bill",
        headers=billing,
        json={"quantity": "2", "payment_method": "cash", "customer_name": "Family"},
    )
    assert billed.status_code == 201, billed.get_json()
    assert billed.get_json()["data"]["bill"]["bill_number"]
    assert Decimal(str(billed.get_json()["data"]["bill"]["taxable_amount"])) == Decimal(
        "29998.00"
    )


def test_billing_cannot_create_package_can_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "travel_agency")

    denied = client.post(
        "/api/v1/tour-packages",
        headers=billing,
        json={"code": "X", "name": "Blocked", "base_price": "100"},
    )
    assert denied.status_code == 403, denied.get_json()

    created = client.post(
        "/api/v1/tour-packages",
        headers=owner,
        json={"code": "KER2N", "name": "Kerala Escape", "base_price": "9999"},
    )
    assert created.status_code == 201, created.get_json()
    pid = created.get_json()["data"]["id"]

    listed = client.get("/api/v1/travel/packages", headers=billing)
    assert listed.status_code == 200, listed.get_json()

    billed = client.post(
        f"/api/v1/tour-packages/{pid}/bill",
        headers=billing,
        json={"payment_method": "cash"},
    )
    assert billed.status_code == 201, billed.get_json()


def test_package_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "travel_agency")
    _switch(client, owner_b, "travel_agency")

    created = client.post(
        "/api/v1/travel/packages",
        headers=owner_a,
        json={"code": "ISO1", "name": "Iso Package", "base_price": "5000"},
    )
    assert created.status_code == 201, created.get_json()
    pid = created.get_json()["data"]["id"]

    assert client.get(f"/api/v1/travel/packages/{pid}", headers=owner_b).status_code == 404
    assert (
        client.patch(
            f"/api/v1/travel/packages/{pid}",
            headers=owner_b,
            json={"name": "Hijack"},
        ).status_code
        == 404
    )
