"""Sprint BIZ-35 — length/weight/area UoM billing (hardware + building material)."""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Pipes"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "450",
        "gst_percentage": "18",
        "stock_quantity": "100",
        "uom": "m",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_pipe_quote_10_times_450_equals_4500(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner)
    pipe = _item(client, owner, cat_id, "GI Pipe 1 inch")

    quote = client.post(
        "/api/v1/hardware/quote",
        headers=billing,
        json={"item_id": pipe["id"], "quantity": "10"},
    )
    assert quote.status_code == 200, quote.get_json()
    body = quote.get_json()["data"]
    assert body["unit_price"] == 450.0
    assert body["line_total"] == 4500.0
    assert body["sale_uom"] == "m"
    assert body["stock_quantity_deducted"] == 10.0
    assert body["sufficient_stock"] is True


def test_hardware_bill_deducts_stock_in_stock_uom(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner, "Steel")
    # Stock kept in metres; sold by foot.
    rod = _item(
        client,
        owner,
        cat_id,
        "MS Rod",
        price="100",
        uom="m",
        sale_uom="ft",
        stock_quantity="50",
    )
    assert rod["sale_uom"] == "ft"
    assert rod["uom"] == "m"

    # 10 ft ≈ 3.048 m
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": rod["id"], "quantity": "10"}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_body = bill.get_json()["data"]
    line = bill_body["items"][0]
    assert Decimal(str(line["quantity"])) == Decimal("10")
    assert Decimal(str(line["unit_price"])) == Decimal("100")
    assert Decimal(str(line["taxable_amount"])) == Decimal("1000.00")

    item = client.get(f"/api/v1/items/{rod['id']}", headers=owner)
    assert item.status_code == 200, item.get_json()
    remaining = Decimal(str(item.get_json()["data"]["stock_quantity"]))
    assert remaining == Decimal("46.952")  # 50 - 3.048


def test_convert_and_units_catalog(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")

    units = client.get("/api/v1/hardware/units", headers=owner)
    assert units.status_code == 200, units.get_json()
    data = units.get_json()["data"]
    assert "m" in data["length_uoms"]
    assert "sqft" in data["area_uoms"]
    assert "kg" in data["weight_uoms"]

    converted = client.post(
        "/api/v1/hardware/convert",
        headers=owner,
        json={"quantity": "2", "from_uom": "sqm", "to_uom": "sqft"},
    )
    assert converted.status_code == 200, converted.get_json()
    assert converted.get_json()["data"]["converted_quantity"] == 21.528


def test_building_material_shares_hardware_apis(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "building_material")
    cat_id = _category(client, owner, "Tiles")
    tile = _item(
        client,
        owner,
        cat_id,
        "Floor Tile",
        price="80",
        uom="sqft",
        sale_uom="sqft",
        stock_quantity="500",
    )

    catalog = client.get("/api/v1/hardware/pos-catalog", headers=billing)
    assert catalog.status_code == 200, catalog.get_json()
    ids = {row["id"] for row in catalog.get_json()["data"]["items"]}
    assert tile["id"] in ids

    quote = client.post(
        "/api/v1/hardware/quote",
        headers=billing,
        json={"item_id": tile["id"], "quantity": "12.5"},
    )
    assert quote.status_code == 200, quote.get_json()
    assert quote.get_json()["data"]["line_total"] == 1000.0


def test_restaurant_denied_hardware_module(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")

    denied = client.get("/api/v1/hardware/units", headers=owner)
    assert denied.status_code == 403, denied.get_json()
