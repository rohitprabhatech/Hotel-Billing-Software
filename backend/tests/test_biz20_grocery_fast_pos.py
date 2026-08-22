"""Sprint BIZ-20 — grocery fast POS and barcode billing."""

from tests.conftest import login


def _switch_grocery(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "grocery_kirana"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Grocery Cat"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "5",
        "stock_quantity": "50",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_grocery_tenant_has_barcode_pos_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert response.status_code == 200, response.get_json()
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "barcode_pos" in enabled


def test_restaurant_tenant_lacks_barcode_pos_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "barcode_pos" not in enabled


def test_pos_catalog_forbidden_for_restaurant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/grocery/pos-catalog", headers=headers)
    assert response.status_code == 403, response.get_json()
    assert response.get_json()["error"]["code"] == "FORBIDDEN"


def test_pos_catalog_returns_weight_flags(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    rice = _item(
        client,
        headers,
        cat_id,
        "Basmati Rice",
        barcode="8907000000001",
        uom="kg",
        price="80",
    )
    _item(client, headers, cat_id, "Soap", barcode="8907000000002", uom="pcs", price="25")

    catalog = client.get("/api/v1/grocery/pos-catalog", headers=headers)
    assert catalog.status_code == 200, catalog.get_json()
    body = catalog.get_json()["data"]
    assert "weight_uoms" in body["scan_defaults"]
    assert "kg" in body["scan_defaults"]["weight_uoms"]

    rice_row = next(row for row in body["items"] if row["id"] == rice["id"])
    assert rice_row["is_weight_uom"] is True
    assert rice_row["barcode"] == "8907000000001"

    soap_row = next(row for row in body["items"] if row["barcode"] == "8907000000002")
    assert soap_row["is_weight_uom"] is False


def test_rapid_barcode_scans_bill_with_merged_qty(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    biscuit = _item(
        client,
        headers,
        cat_id,
        "Parle-G",
        barcode="8907000000010",
        uom="pcs",
        price="10",
        stock_quantity="100",
    )

    found = client.get("/api/v1/items/by-barcode/8907000000010", headers=headers)
    assert found.status_code == 200, found.get_json()
    assert found.get_json()["data"]["id"] == biscuit["id"]

    bill = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": biscuit["id"], "quantity": "3"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_data = bill.get_json()["data"]
    assert len(bill_data["items"]) == 1
    assert float(bill_data["items"][0]["quantity"]) == 3.0
    assert bill_data["bill_number"]


def test_decimal_weight_qty_bill(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    dal = _item(
        client,
        headers,
        cat_id,
        "Toor Dal",
        barcode="8907000000020",
        uom="kg",
        price="120",
        stock_quantity="10",
    )

    bill = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": dal["id"], "quantity": "0.750"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_data = bill.get_json()["data"]
    line = bill_data["items"][0]
    assert float(line["quantity"]) == 0.75
    assert float(bill_data["subtotal"]) == 90.0

    after = client.get(f"/api/v1/items/{dal['id']}", headers=headers).get_json()["data"]
    assert float(after["stock_quantity"]) == 9.25


def test_insufficient_stock_blocks_grocery_bill(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    item = _item(
        client,
        headers,
        cat_id,
        "Milk Pouch",
        barcode="8907000000030",
        uom="l",
        price="60",
        stock_quantity="2",
    )

    blocked = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": "2.5"}],
        },
    )
    assert blocked.status_code == 400, blocked.get_json()
    assert blocked.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"

    still = client.get(f"/api/v1/items/{item['id']}", headers=headers).get_json()["data"]
    assert float(still["stock_quantity"]) == 2.0


def test_pos_catalog_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_grocery(client, owner_a)
    cat_id = _category(client, owner_a)
    secret = _item(
        client,
        owner_a,
        cat_id,
        "Tenant A Only",
        barcode="8907000000040",
    )

    denied = client.get("/api/v1/grocery/pos-catalog", headers=owner_b)
    assert denied.status_code == 403, denied.get_json()

    catalog_a = client.get("/api/v1/grocery/pos-catalog", headers=owner_a)
    assert catalog_a.status_code == 200, catalog_a.get_json()
    ids = {row["id"] for row in catalog_a.get_json()["data"]["items"]}
    assert secret["id"] in ids
