"""Sprint BIZ-44 — stationery pack on shared barcode POS."""

from tests.conftest import login


def _switch(client, headers, business_type="stationery"):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Stationery Cat"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "25",
        "gst_percentage": "12",
        "stock_quantity": "40",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_stationery_module_flags(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in ("barcode_pos", "bulk_pricing", "customer_credit"):
        assert code in modules, code
    assert "batch_expiry" not in modules
    assert "serial_imei" not in modules


def test_stationery_pos_catalog_and_search(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    pen = _item(
        client,
        owner,
        cat_id,
        "Blue Ball Pen",
        barcode="8908111000001",
        sku="PEN-BLU",
        price="10",
        stock_quantity="100",
    )
    _item(client, owner, cat_id, "A4 Notebook", barcode="8908111000002", sku="NB-A4")

    catalog = client.get("/api/v1/stationery/pos-catalog", headers=billing)
    assert catalog.status_code == 200, catalog.get_json()
    assert catalog.get_json()["success"] is True
    assert catalog.get_json()["data"]["bulk_pricing_enabled"] is True
    ids = {row["id"] for row in catalog.get_json()["data"]["items"]}
    assert pen["id"] in ids

    search = client.get(
        "/api/v1/stationery/products/search",
        headers=billing,
        query_string={"q": "Ball Pen"},
    )
    assert search.status_code == 200, search.get_json()
    names = {row["name"] for row in search.get_json()["data"]["items"]}
    assert "Blue Ball Pen" in names

    by_code = client.get(
        "/api/v1/stationery/products/by-barcode/8908111000001",
        headers=billing,
    )
    assert by_code.status_code == 200, by_code.get_json()
    assert by_code.get_json()["data"]["id"] == pen["id"]


def test_stationery_barcode_bill_and_credit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    cat_id = _category(client, owner, "Bill Cat")
    eraser = _item(
        client,
        owner,
        cat_id,
        "Soft Eraser",
        barcode="8908111000099",
        price="5",
        gst_percentage="0",
        stock_quantity="20",
        minimum_stock_level="5",
    )
    customer = client.post(
        "/api/v1/customers",
        headers=owner,
        json={"name": "School Mart", "phone_country_code": "91", "phone": "9000000044"},
    ).get_json()["data"]

    cash = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": eraser["id"], "quantity": "3"}],
        },
    )
    assert cash.status_code == 201, cash.get_json()
    assert cash.get_json()["data"]["grand_total"] == 15.0

    credit = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": eraser["id"], "quantity": "2"}],
        },
    )
    assert credit.status_code == 201, credit.get_json()

    outstanding = client.get("/api/v1/customers/outstanding", headers=owner)
    assert outstanding.status_code == 200, outstanding.get_json()
    match = next(row for row in outstanding.get_json()["data"] if row["id"] == customer["id"])
    assert float(match["balance"]) == 10.0

    stock = client.get(f"/api/v1/items/{eraser['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 15.0


def test_stationery_forbidden_for_restaurant(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/stationery/pos-catalog", headers=owner).status_code == 403
