"""Sprint BIZ-38 — multi-warehouse stock foundation."""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Yard"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name="Cement", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "50",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_transfer_conserves_quantity_between_warehouses(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, stock_quantity="40")

    listing = client.get("/api/v1/warehouses", headers=owner)
    assert listing.status_code == 200, listing.get_json()
    warehouses = listing.get_json()["data"]
    assert any(row["is_default"] for row in warehouses)
    main = next(row for row in warehouses if row["is_default"])

    yard = client.post(
        "/api/v1/warehouses",
        headers=owner,
        json={"code": "YARD", "name": "Site yard"},
    )
    assert yard.status_code == 201, yard.get_json()
    yard_id = yard.get_json()["data"]["id"]

    transfer = client.post(
        "/api/v1/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": yard_id,
            "items": [{"item_id": item["id"], "quantity": "15"}],
        },
    )
    assert transfer.status_code == 201, transfer.get_json()
    assert transfer.get_json()["data"]["transfer_number"].startswith("ST-")

    stocks = client.get(
        "/api/v1/warehouses/stocks",
        headers=owner,
        query_string={"item_id": item["id"]},
    )
    assert stocks.status_code == 200, stocks.get_json()
    by_wh = {row["warehouse_id"]: Decimal(str(row["quantity"])) for row in stocks.get_json()["data"]}
    assert by_wh[main["id"]] == Decimal("25")
    assert by_wh[yard_id] == Decimal("15")
    assert sum(by_wh.values()) == Decimal("40")

    item_view = client.get(f"/api/v1/items/{item['id']}", headers=owner)
    assert Decimal(str(item_view.get_json()["data"]["stock_quantity"])) == Decimal("40")


def test_sell_from_selected_warehouse(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, stock_quantity="20")

    warehouses = client.get("/api/v1/warehouses", headers=owner).get_json()["data"]
    main = next(row for row in warehouses if row["is_default"])
    site = client.post(
        "/api/v1/warehouses",
        headers=owner,
        json={"code": "SITE", "name": "Site store"},
    ).get_json()["data"]

    client.post(
        "/api/v1/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": site["id"],
            "items": [{"item_id": item["id"], "quantity": "8"}],
        },
    )

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "5"}],
            "payment_method": "cash",
            "warehouse_id": site["id"],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert bill.get_json()["data"]["warehouse_id"] == site["id"]

    stocks = client.get(
        "/api/v1/warehouses/stocks",
        headers=owner,
        query_string={"item_id": item["id"]},
    ).get_json()["data"]
    by_wh = {row["warehouse_id"]: Decimal(str(row["quantity"])) for row in stocks}
    assert by_wh[site["id"]] == Decimal("3")
    assert by_wh[main["id"]] == Decimal("12")

    item_view = client.get(f"/api/v1/items/{item['id']}", headers=owner)
    assert Decimal(str(item_view.get_json()["data"]["stock_quantity"])) == Decimal("15")


def test_oversell_from_warehouse_blocked(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, stock_quantity="10")
    warehouses = client.get("/api/v1/warehouses", headers=owner).get_json()["data"]
    main = next(row for row in warehouses if row["is_default"])
    other = client.post(
        "/api/v1/warehouses",
        headers=owner,
        json={"code": "B2", "name": "Bay 2"},
    ).get_json()["data"]
    client.post(
        "/api/v1/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": other["id"],
            "items": [{"item_id": item["id"], "quantity": "3"}],
        },
    )

    # Item still has 10 total, but warehouse other only has 3.
    denied = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "5"}],
            "payment_method": "cash",
            "warehouse_id": other["id"],
        },
    )
    assert denied.status_code == 400, denied.get_json()


def test_restaurant_denied_warehouses(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/warehouses", headers=owner).status_code == 403
