"""Sprint BIZ-08 — barcode and unit-of-measure foundations."""

from decimal import Decimal

from tests.conftest import login


def _create_category(client, headers, name="Barcode Category"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _create_item(client, headers, category_id, **overrides):
    payload = {
        "name": "Barcode Item",
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "5",
        "barcode": "8901234567890",
        "uom": "kg",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_create_item_with_barcode_and_uom(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, headers)
    item = _create_item(client, headers, category_id)
    assert item["barcode"] == "8901234567890"
    assert item["uom"] == "kg"


def test_duplicate_barcode_rejected(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, headers)
    _create_item(client, headers, category_id, name="Item A", barcode="8901111111111")

    dup = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": "Item B",
            "category_id": category_id,
            "price": "50",
            "gst_percentage": "5",
            "barcode": "8901111111111",
        },
    )
    assert dup.status_code == 409, dup.get_json()


def test_get_item_by_barcode(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, headers)
    created = _create_item(client, headers, category_id, barcode="8902222222222")

    found = client.get("/api/v1/items/by-barcode/8902222222222", headers=headers)
    assert found.status_code == 200, found.get_json()
    assert found.get_json()["data"]["id"] == created["id"]


def test_list_items_by_barcode_query(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, headers)
    created = _create_item(client, headers, category_id, barcode="8903333333333")

    listing = client.get("/api/v1/items", headers=headers, query_string={"barcode": "8903333333333"})
    assert listing.status_code == 200, listing.get_json()
    rows = listing.get_json()["data"]
    assert len(rows) == 1
    assert rows[0]["id"] == created["id"]


def test_search_includes_barcode(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, headers)
    _create_item(client, headers, category_id, name="Rice Bag", barcode="8904444444444")

    listing = client.get("/api/v1/items", headers=headers, query_string={"q": "8904444"})
    assert listing.status_code == 200, listing.get_json()
    assert any(row["barcode"] == "8904444444444" for row in listing.get_json()["data"])


def test_barcode_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    category_id = _create_category(client, owner_a)
    _create_item(client, owner_a, category_id, barcode="8905555555555")

    denied = client.get("/api/v1/items/by-barcode/8905555555555", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_uom_conversion_helpers():
    from app.utils.uom import convert_quantity

    assert convert_quantity(1, "kg", "g") == Decimal("1000")
    assert convert_quantity(500, "g", "kg") == Decimal("0.500")
    assert convert_quantity(2, "l", "ml") == Decimal("2000")
