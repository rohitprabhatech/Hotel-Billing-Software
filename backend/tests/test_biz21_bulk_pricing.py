"""Sprint BIZ-21 — grocery multi-unit stock and bulk price tiers."""

from tests.conftest import login


def _switch_grocery(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "grocery_kirana"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Bulk Cat"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "100",
        "uom": "kg",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_grocery_has_bulk_pricing_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    modules = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert modules.status_code == 200
    assert "bulk_pricing" in modules.get_json()["data"]["enabled_modules"]


def test_restaurant_price_tiers_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Resto Bulk")
    item = _item(client, headers, cat_id, "No Tier Item", uom="pcs")
    denied = client.get(f"/api/v1/items/{item['id']}/price-tiers", headers=headers)
    assert denied.status_code == 403, denied.get_json()
    assert denied.get_json()["error"]["code"] == "FORBIDDEN"


def test_replace_tiers_and_boundaries(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    rice = _item(
        client,
        headers,
        cat_id,
        "Bulk Rice",
        barcode="8908000000001",
        price="100",
        stock_quantity="50",
    )

    replaced = client.put(
        f"/api/v1/items/{rice['id']}/price-tiers",
        headers=headers,
        json={
            "tiers": [
                {"min_quantity": "5", "unit_price": "90"},
                {"min_quantity": "10", "unit_price": "80"},
            ]
        },
    )
    assert replaced.status_code == 200, replaced.get_json()
    tiers = replaced.get_json()["data"]
    assert len(tiers) == 2
    assert float(tiers[0]["min_quantity"]) == 5.0
    assert float(tiers[1]["unit_price"]) == 80.0

    listing = client.get(f"/api/v1/items/{rice['id']}/price-tiers", headers=headers)
    assert listing.status_code == 200
    assert len(listing.get_json()["data"]) == 2


def test_bill_applies_tier_at_boundary(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    dal = _item(
        client,
        headers,
        cat_id,
        "Toor Dal Bulk",
        barcode="8908000000010",
        price="120",
        gst_percentage="0",
        stock_quantity="100",
        uom="kg",
    )
    client.put(
        f"/api/v1/items/{dal['id']}/price-tiers",
        headers=headers,
        json={
            "tiers": [
                {"min_quantity": "2", "unit_price": "110"},
                {"min_quantity": "5", "unit_price": "100"},
            ]
        },
    )

    # Below first tier → base 120
    bill_low = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": dal["id"], "quantity": "1"}],
        },
    )
    assert bill_low.status_code == 201, bill_low.get_json()
    low = bill_low.get_json()["data"]
    assert float(low["items"][0]["unit_price"]) == 120.0
    assert float(low["subtotal"]) == 120.0

    # Exactly min_quantity 2 → 110
    bill_mid = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": dal["id"], "quantity": "2"}],
        },
    )
    assert bill_mid.status_code == 201, bill_mid.get_json()
    mid = bill_mid.get_json()["data"]
    assert float(mid["items"][0]["unit_price"]) == 110.0
    assert float(mid["subtotal"]) == 220.0

    # Qty 5 → 100
    bill_high = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": dal["id"], "quantity": "5"}],
        },
    )
    assert bill_high.status_code == 201, bill_high.get_json()
    high = bill_high.get_json()["data"]
    assert float(high["items"][0]["unit_price"]) == 100.0
    assert float(high["subtotal"]) == 500.0


def test_pos_catalog_includes_tiers(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    item = _item(client, headers, cat_id, "Sugar Bulk", barcode="8908000000020", price="50")
    client.put(
        f"/api/v1/items/{item['id']}/price-tiers",
        headers=headers,
        json={"tiers": [{"min_quantity": "3", "unit_price": "45"}]},
    )

    catalog = client.get("/api/v1/grocery/pos-catalog", headers=headers)
    assert catalog.status_code == 200, catalog.get_json()
    body = catalog.get_json()["data"]
    assert body["bulk_pricing_enabled"] is True
    row = next(r for r in body["items"] if r["id"] == item["id"])
    assert len(row["price_tiers"]) == 1
    assert float(row["price_tiers"][0]["unit_price"]) == 45.0


def test_duplicate_min_quantity_rejected(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    item = _item(client, headers, cat_id, "Oil Bulk", price="200")
    bad = client.put(
        f"/api/v1/items/{item['id']}/price-tiers",
        headers=headers,
        json={
            "tiers": [
                {"min_quantity": "5", "unit_price": "180"},
                {"min_quantity": "5", "unit_price": "170"},
            ]
        },
    )
    assert bad.status_code == 400, bad.get_json()


def test_delete_tier(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    item = _item(client, headers, cat_id, "Salt Bulk", price="20")
    created = client.post(
        f"/api/v1/items/{item['id']}/price-tiers",
        headers=headers,
        json={"min_quantity": "10", "unit_price": "18"},
    )
    assert created.status_code == 201, created.get_json()
    tier_id = created.get_json()["data"]["id"]

    deleted = client.delete(
        f"/api/v1/items/{item['id']}/price-tiers/{tier_id}",
        headers=headers,
    )
    assert deleted.status_code == 200, deleted.get_json()
    listing = client.get(f"/api/v1/items/{item['id']}/price-tiers", headers=headers)
    assert listing.get_json()["data"] == []
