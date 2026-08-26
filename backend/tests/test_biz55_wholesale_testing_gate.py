"""Sprint BIZ-55 — wholesale testing gate.

Regression matrix across BIZ-51 … BIZ-54: price lists, SO/PO, warehouses,
aged outstanding, challans / tax invoice, module matrix, isolation,
permissions, audit, and API contracts.

Run full phase gate from backend/:
  python -m pytest tests/test_biz51_wholesale_price_lists.py \\
    tests/test_biz52_sales_purchase_orders.py \\
    tests/test_biz53_wholesale_warehouse.py \\
    tests/test_biz54_wholesale_outstanding.py \\
    tests/test_biz55_wholesale_testing_gate.py -q
"""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type: str):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Gate Wholesale"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name="Gate Carton", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "50",
        "uom": "pcs",
        "cost_price": "60",
        "minimum_stock_level": "5",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _customer(client, headers, name="Gate Dealer", phone="9000000071"):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": phone},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _supplier(client, headers, name="Gate Mill"):
    response = client.post("/api/v1/suppliers", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_restaurant_wholesale_vertical_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    for path in (
        "/api/v1/price-lists",
        "/api/v1/wholesale/price-lists",
        "/api/v1/sales-orders",
        "/api/v1/purchase-orders",
        "/api/v1/warehouses",
        "/api/v1/wholesale/warehouses",
        "/api/v1/challans",
        "/api/v1/wholesale/challans",
    ):
        assert client.get(path, headers=owner).status_code == 403, path


def test_gate_module_matrix_wholesale(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in (
        "price_lists",
        "sales_orders",
        "purchase_orders",
        "warehouse",
        "customer_credit",
        "quotation",
        "delivery_challan",
        "barcode_pos",
        "bulk_pricing",
    ):
        assert code in modules, code
    for code in (
        "furniture_attributes",
        "serial_imei",
        "production",
        "order_channels",
        "book_metadata",
    ):
        assert code not in modules, code


def test_gate_price_list_so_warehouse_outstanding_flow(client):
    """Happy path tying BIZ-51…54 together."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, stock_quantity="30")
    buyer = _customer(client, owner)

    wholesale = client.post(
        "/api/v1/wholesale/price-lists",
        headers=owner,
        json={"name": "Gate Wholesale", "list_type": "WHOLESALE", "is_default": True},
    )
    assert wholesale.status_code == 201, wholesale.get_json()
    list_id = wholesale.get_json()["data"]["id"]
    assert "CREATE_PRICE_LIST" in _audit_actions(client, owner, action="CREATE_PRICE_LIST")

    put_items = client.put(
        f"/api/v1/price-lists/{list_id}/items",
        headers=owner,
        json={"items": [{"item_id": item["id"], "unit_price": "80"}]},
    )
    assert put_items.status_code == 200, put_items.get_json()

    so = client.post(
        "/api/v1/wholesale/sales-orders",
        headers=owner,
        json={
            "customer_id": buyer["id"],
            "customer_name": buyer["name"],
            "items": [{"item_id": item["id"], "quantity": "3"}],
        },
    )
    assert so.status_code == 201, so.get_json()
    so_id = so.get_json()["data"]["id"]
    assert so.get_json()["data"]["order_number"].startswith("SO-")
    assert "CREATE_SALES_ORDER" in _audit_actions(client, owner, action="CREATE_SALES_ORDER")

    confirmed = client.patch(
        f"/api/v1/sales-orders/{so_id}/status",
        headers=owner,
        json={"status": "CONFIRMED"},
    )
    assert confirmed.status_code == 200, confirmed.get_json()

    converted = client.post(
        f"/api/v1/wholesale/sales-orders/{so_id}/convert",
        headers=owner,
        json={"payment_method": "credit"},
    )
    assert converted.status_code == 200, converted.get_json()
    bill = converted.get_json()["data"]["bill"]
    # List price 80 × 3
    assert Decimal(str(bill["grand_total"])) == Decimal("240")
    assert bill["payment_method"] == "credit"

    warehouses = client.get("/api/v1/wholesale/warehouses", headers=owner).get_json()["data"]
    main = next(row for row in warehouses if row["is_default"])
    bay = client.post(
        "/api/v1/wholesale/warehouses",
        headers=owner,
        json={"code": "GATE2", "name": "Gate Bay 2"},
    )
    assert bay.status_code == 201, bay.get_json()
    assert "CREATE_WAREHOUSE" in _audit_actions(client, owner, action="CREATE_WAREHOUSE")
    bay_id = bay.get_json()["data"]["id"]

    transfer = client.post(
        "/api/v1/wholesale/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": bay_id,
            "items": [{"item_id": item["id"], "quantity": "5"}],
        },
    )
    assert transfer.status_code == 201, transfer.get_json()
    assert "CREATE_STOCK_TRANSFER" in _audit_actions(
        client, owner, action="CREATE_STOCK_TRANSFER"
    )

    sell = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "2"}],
            "payment_method": "cash",
            "warehouse_id": bay_id,
            "customer_id": buyer["id"],
        },
    )
    assert sell.status_code == 201, sell.get_json()
    assert sell.get_json()["data"]["warehouse_id"] == bay_id

    outstanding = client.get("/api/v1/reports/outstanding", headers=owner)
    assert outstanding.status_code == 200, outstanding.get_json()
    parties = outstanding.get_json()["data"]["customers"]["parties"]
    match = next(row for row in parties if row["id"] == buyer["id"])
    assert Decimal(str(match["balance"])) == Decimal("240")
    assert Decimal(str(match["aging"]["0_30"])) == Decimal("240")

    challan = client.post(
        "/api/v1/wholesale/challans",
        headers=owner,
        json={
            "customer_name": buyer["name"],
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert challan.status_code == 201, challan.get_json()
    assert "CREATE_DELIVERY_CHALLAN" in _audit_actions(
        client, owner, action="CREATE_DELIVERY_CHALLAN"
    )


def test_gate_purchase_order_convert(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner, "Gate PO")
    item = _item(client, owner, cat_id, name="Gate PO Item", stock_quantity="5")
    supplier = _supplier(client, owner)

    created = client.post(
        "/api/v1/wholesale/purchase-orders",
        headers=owner,
        json={
            "supplier_id": supplier["id"],
            "items": [{"item_id": item["id"], "quantity": "4", "unit_cost": "55"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    po_id = created.get_json()["data"]["id"]
    assert created.get_json()["data"]["order_number"].startswith("PO-")
    assert "CREATE_PURCHASE_ORDER" in _audit_actions(
        client, owner, action="CREATE_PURCHASE_ORDER"
    )

    client.patch(
        f"/api/v1/purchase-orders/{po_id}/status",
        headers=owner,
        json={"status": "CONFIRMED"},
    )
    converted = client.post(
        f"/api/v1/wholesale/purchase-orders/{po_id}/convert",
        headers=owner,
        json={},
    )
    assert converted.status_code == 200, converted.get_json()
    stock = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert Decimal(str(stock["stock_quantity"])) == Decimal("9")


def test_gate_billing_permissions(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner, "Gate Perm")
    item = _item(client, owner, cat_id, name="Perm Item")
    buyer = _customer(client, owner, name="Perm Buyer", phone="9000000072")

    assert (
        client.post(
            "/api/v1/price-lists",
            headers=billing,
            json={"name": "Blocked", "list_type": "WHOLESALE"},
        ).status_code
        == 403
    )
    assert client.get("/api/v1/price-lists", headers=billing).status_code == 200

    assert (
        client.post(
            "/api/v1/sales-orders",
            headers=billing,
            json={
                "customer_id": buyer["id"],
                "items": [{"item_id": item["id"], "quantity": "1"}],
            },
        ).status_code
        == 403
    )
    assert client.get("/api/v1/sales-orders", headers=billing).status_code == 200

    assert (
        client.post(
            "/api/v1/warehouses",
            headers=billing,
            json={"code": "X", "name": "Blocked"},
        ).status_code
        == 403
    )
    assert client.get("/api/v1/warehouses", headers=billing).status_code == 200

    assert client.get("/api/v1/reports/outstanding", headers=billing).status_code in (
        403,
        401,
    )
    assert client.get("/api/v1/challans", headers=billing).status_code == 200
    assert (
        client.post(
            "/api/v1/challans",
            headers=billing,
            json={
                "customer_name": "Blocked",
                "items": [{"item_id": item["id"], "quantity": "1"}],
            },
        ).status_code
        == 403
    )


def test_gate_cross_tenant_wholesale_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "wholesale")
    _switch(client, owner_b, "wholesale")

    cat_id = _category(client, owner_a, "Iso WH")
    item = _item(client, owner_a, cat_id, name="Iso Carton")
    buyer = _customer(client, owner_a, name="Iso Dealer", phone="9000000073")

    pl = client.post(
        "/api/v1/price-lists",
        headers=owner_a,
        json={"name": "Iso List", "list_type": "WHOLESALE"},
    ).get_json()["data"]
    so = client.post(
        "/api/v1/sales-orders",
        headers=owner_a,
        json={
            "customer_id": buyer["id"],
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]
    wh = client.post(
        "/api/v1/warehouses",
        headers=owner_a,
        json={"code": "ISO", "name": "Iso Store"},
    ).get_json()["data"]
    challan = client.post(
        "/api/v1/challans",
        headers=owner_a,
        json={
            "customer_name": "Iso",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    assert client.get(f"/api/v1/price-lists/{pl['id']}", headers=owner_b).status_code == 404
    assert client.get(f"/api/v1/sales-orders/{so['id']}", headers=owner_b).status_code == 404
    assert client.patch(
        f"/api/v1/warehouses/{wh['id']}",
        headers=owner_b,
        json={"name": "Hijack"},
    ).status_code in (404, 403)
    assert client.get(f"/api/v1/challans/{challan['id']}", headers=owner_b).status_code == 404


def test_gate_api_envelopes(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    for path in (
        "/api/v1/wholesale/price-lists",
        "/api/v1/wholesale/sales-orders",
        "/api/v1/wholesale/purchase-orders",
        "/api/v1/wholesale/warehouses",
        "/api/v1/wholesale/challans",
        "/api/v1/wholesale/reports/outstanding",
        "/api/v1/reports/outstanding",
    ):
        response = client.get(path, headers=owner)
        assert response.status_code == 200, path
        body = response.get_json()
        assert body["success"] is True, path
        assert "data" in body, path
