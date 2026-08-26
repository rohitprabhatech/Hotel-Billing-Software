"""Sprint BIZ-53 — wholesale multi-warehouse & stock transfer."""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Bay"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name="Carton", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "40",
        "uom": "pcs",
        "minimum_stock_level": "5",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_wholesale_module_has_warehouse(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    assert "warehouse" in modules


def test_wholesale_warehouse_aliases_and_default_seed(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    _item(client, owner, cat_id, stock_quantity="25")

    listing = client.get("/api/v1/wholesale/warehouses", headers=owner)
    assert listing.status_code == 200, listing.get_json()
    warehouses = listing.get_json()["data"]
    assert any(row["is_default"] for row in warehouses)
    assert any(row["code"] == "MAIN" for row in warehouses)

    stocks = client.get("/api/v1/wholesale/warehouses/stocks", headers=owner)
    assert stocks.status_code == 200, stocks.get_json()
    assert any(Decimal(str(row["quantity"])) == Decimal("25") for row in stocks.get_json()["data"])


def test_wholesale_sell_from_selected_warehouse(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, stock_quantity="20")

    warehouses = client.get("/api/v1/wholesale/warehouses", headers=owner).get_json()["data"]
    main = next(row for row in warehouses if row["is_default"])
    bay = client.post(
        "/api/v1/wholesale/warehouses",
        headers=owner,
        json={"code": "BAY2", "name": "Bay 2"},
    )
    assert bay.status_code == 201, bay.get_json()
    bay_id = bay.get_json()["data"]["id"]

    transfer = client.post(
        "/api/v1/wholesale/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": bay_id,
            "items": [{"item_id": item["id"], "quantity": "8"}],
        },
    )
    assert transfer.status_code == 201, transfer.get_json()
    assert transfer.get_json()["data"]["transfer_number"].startswith("ST-")

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "5"}],
            "payment_method": "cash",
            "warehouse_id": bay_id,
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert bill.get_json()["data"]["warehouse_id"] == bay_id

    stocks = client.get(
        "/api/v1/wholesale/warehouses/stocks",
        headers=owner,
        query_string={"item_id": item["id"]},
    ).get_json()["data"]
    by_wh = {row["warehouse_id"]: Decimal(str(row["quantity"])) for row in stocks}
    assert by_wh[bay_id] == Decimal("3")
    assert by_wh[main["id"]] == Decimal("12")

    item_view = client.get(f"/api/v1/items/{item['id']}", headers=owner)
    assert Decimal(str(item_view.get_json()["data"]["stock_quantity"])) == Decimal("15")


def test_transfer_rejects_insufficient_source_before_any_move(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item_a = _item(client, owner, cat_id, name="Alpha", stock_quantity="10")
    item_b = _item(client, owner, cat_id, name="Beta", stock_quantity="10")

    warehouses = client.get("/api/v1/warehouses", headers=owner).get_json()["data"]
    main = next(row for row in warehouses if row["is_default"])
    other = client.post(
        "/api/v1/warehouses",
        headers=owner,
        json={"code": "COLD", "name": "Cold store"},
    ).get_json()["data"]

    denied = client.post(
        "/api/v1/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": other["id"],
            "items": [
                {"item_id": item_a["id"], "quantity": "4"},
                {"item_id": item_b["id"], "quantity": "99"},
            ],
        },
    )
    assert denied.status_code == 400, denied.get_json()
    assert "Insufficient stock" in (denied.get_json()["error"]["message"] or "")

    stocks = client.get(
        "/api/v1/warehouses/stocks",
        headers=owner,
        query_string={"warehouse_id": main["id"]},
    ).get_json()["data"]
    by_item = {row["item_id"]: Decimal(str(row["quantity"])) for row in stocks}
    assert by_item[item_a["id"]] == Decimal("10")
    assert by_item[item_b["id"]] == Decimal("10")


def test_warehouse_low_stock_notification_on_sale(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item = _item(
        client,
        owner,
        cat_id,
        name="Notify Carton",
        stock_quantity="8",
        minimum_stock_level="5",
    )

    warehouses = client.get("/api/v1/warehouses", headers=owner).get_json()["data"]
    main = next(row for row in warehouses if row["is_default"])

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "4"}],
            "payment_method": "cash",
            "warehouse_id": main["id"],
        },
    )
    assert bill.status_code == 201, bill.get_json()

    notes = client.get(
        "/api/v1/notifications", headers=owner, query_string={"per_page": 100}
    ).get_json()["data"]
    wh_low = [
        n
        for n in notes
        if n["type"] == "LOW_STOCK"
        and n.get("entity_type") == "WAREHOUSE_STOCK"
        and "Notify Carton" in (n.get("message") or "")
    ]
    assert wh_low, notes
