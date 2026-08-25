"""Sprint BIZ-25 — clothing size/color/brand variants."""

from tests.conftest import login


def _switch_clothing(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Apparel"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "499",
        "gst_percentage": "0",
        "stock_quantity": "10",
        "uom": "pcs",
        "minimum_stock_level": "2",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_clothing_has_variants_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    modules = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert modules.status_code == 200
    assert "variants" in modules.get_json()["data"]["enabled_modules"]


def test_restaurant_variants_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "No Variants")
    item = _item(client, headers, cat_id, "Plain Shirt")
    denied = client.get(f"/api/v1/items/{item['id']}/variants", headers=headers)
    assert denied.status_code == 403, denied.get_json()
    assert denied.get_json()["error"]["code"] == "FORBIDDEN"


def test_create_variant_unique_size_color(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers)
    shirt = _item(client, headers, cat_id, "Oxford Shirt", stock_quantity="8")

    created = client.post(
        f"/api/v1/items/{shirt['id']}/variants",
        headers=headers,
        json={"size": "M", "color": "Blue", "brand": "House", "sku": "OX-M-BLU"},
    )
    assert created.status_code == 201, created.get_json()
    data = created.get_json()["data"]
    assert data["size"] == "M"
    assert data["color"] == "Blue"
    assert float(data["stock_quantity"]) == 8.0

    clash = client.post(
        f"/api/v1/items/{shirt['id']}/variants",
        headers=headers,
        json={"size": "m", "color": "blue", "stock_quantity": "3"},
    )
    assert clash.status_code == 409, clash.get_json()

    other = client.post(
        f"/api/v1/items/{shirt['id']}/variants",
        headers=headers,
        json={"size": "L", "color": "Blue", "stock_quantity": "5", "barcode": "8909000000001"},
    )
    assert other.status_code == 201, other.get_json()

    listing = client.get(f"/api/v1/items/{shirt['id']}/variants", headers=headers)
    assert listing.status_code == 200
    assert len(listing.get_json()["data"]) == 2

    refreshed = client.get(f"/api/v1/items/{shirt['id']}", headers=headers)
    assert refreshed.status_code == 200
    assert refreshed.get_json()["data"]["tracks_variants"] is True
    assert float(refreshed.get_json()["data"]["stock_quantity"]) == 13.0


def test_sell_reduces_only_that_variant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers)
    tee = _item(client, headers, cat_id, "Cotton Tee", stock_quantity="0")
    medium = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "M", "color": "Black", "stock_quantity": "4"},
    ).get_json()["data"]
    large = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "L", "color": "Black", "stock_quantity": "6"},
    ).get_json()["data"]

    missing = client.post(
        "/api/v1/bills",
        headers=headers,
        json={"payment_method": "cash", "items": [{"item_id": tee["id"], "quantity": "1"}]},
    )
    assert missing.status_code == 400, missing.get_json()

    wrong = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": tee["id"], "variant_id": large["id"] + "x", "quantity": "1"}],
        },
    )
    assert wrong.status_code == 400, wrong.get_json()

    bill = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": tee["id"], "variant_id": medium["id"], "quantity": "2"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    line = bill.get_json()["data"]["items"][0]
    assert line["variant_id"] == medium["id"]
    assert "M/Black" in line["item_name"] or "M / Black" in line["item_name"]

    rows = client.get(f"/api/v1/items/{tee['id']}/variants", headers=headers).get_json()["data"]
    by_id = {row["id"]: row for row in rows}
    assert float(by_id[medium["id"]]["stock_quantity"]) == 2.0
    assert float(by_id[large["id"]]["stock_quantity"]) == 6.0

    parent = client.get(f"/api/v1/items/{tee['id']}", headers=headers).get_json()["data"]
    assert float(parent["stock_quantity"]) == 8.0


def test_wrong_item_variant_blocked_and_cancel_restocks(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers)
    a = _item(client, headers, cat_id, "Kurta A", stock_quantity="0")
    b = _item(client, headers, cat_id, "Kurta B", stock_quantity="0")
    va = client.post(
        f"/api/v1/items/{a['id']}/variants",
        headers=headers,
        json={"size": "S", "color": "Red", "stock_quantity": "3"},
    ).get_json()["data"]
    vb = client.post(
        f"/api/v1/items/{b['id']}/variants",
        headers=headers,
        json={"size": "S", "color": "Red", "stock_quantity": "9"},
    ).get_json()["data"]

    crossed = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": a["id"], "variant_id": vb["id"], "quantity": "1"}],
        },
    )
    assert crossed.status_code == 400, crossed.get_json()

    billed = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": a["id"], "variant_id": va["id"], "quantity": "1"}],
        },
    )
    assert billed.status_code == 201, billed.get_json()
    bill_id = billed.get_json()["data"]["id"]

    cancel = client.post(
        f"/api/v1/bills/{bill_id}/cancel",
        headers=headers,
        json={"reason": "Customer exchange later"},
    )
    assert cancel.status_code == 200, cancel.get_json()
    restored = client.get(f"/api/v1/items/{a['id']}/variants", headers=headers).get_json()["data"]
    assert float(restored[0]["stock_quantity"]) == 3.0


def test_variant_isolation_and_barcode(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_clothing(client, owner_a)
    _switch_clothing(client, owner_b)

    cat_a = _category(client, owner_a, "A Wear")
    item_a = _item(client, owner_a, cat_a, "Isolated Tee", stock_quantity="0")
    variant = client.post(
        f"/api/v1/items/{item_a['id']}/variants",
        headers=owner_a,
        json={
            "size": "XL",
            "color": "Green",
            "stock_quantity": "2",
            "barcode": "8909000000099",
        },
    ).get_json()["data"]

    denied = client.get(f"/api/v1/items/{item_a['id']}/variants", headers=owner_b)
    assert denied.status_code in {403, 404}, denied.get_json()

    lookup = client.get("/api/v1/items/by-barcode/8909000000099", headers=owner_a)
    assert lookup.status_code == 200, lookup.get_json()
    body = lookup.get_json()["data"]
    assert body["id"] == item_a["id"]
    assert body["matched_variant"]["id"] == variant["id"]

    other = client.get("/api/v1/items/by-barcode/8909000000099", headers=owner_b)
    assert other.status_code == 404, other.get_json()
