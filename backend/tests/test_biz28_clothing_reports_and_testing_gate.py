"""Sprint BIZ-28 — clothing reports and clothing testing gate.

Brand/size/category sales, customer history, isolation, permissions, returns,
audit, and API contracts across BIZ-25 … BIZ-27.

Run full phase gate from backend/:
  python -m pytest tests/test_biz25_clothing_variants.py tests/test_biz26_clothing_images_pos.py
    tests/test_biz27_clothing_returns.py tests/test_biz28_clothing_reports_and_testing_gate.py -q
"""

from tests.conftest import login


def _switch_clothing(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "200",
        "gst_percentage": "0",
        "stock_quantity": "0",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _variant(client, headers, item_id, **payload):
    response = client.post(f"/api/v1/items/{item_id}/variants", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _customer(client, headers, name, phone):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": phone},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _sell(client, headers, item_id, variant_id, quantity="1", customer_id=None):
    body = {
        "payment_method": "cash",
        "items": [{"item_id": item_id, "variant_id": variant_id, "quantity": quantity}],
    }
    if customer_id:
        body["customer_id"] = customer_id
    billed = client.post("/api/v1/bills", headers=headers, json=body)
    assert billed.status_code == 201, billed.get_json()
    return billed.get_json()["data"]


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_restaurant_clothing_reports_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    denied = client.get("/api/v1/clothing/sales", headers=headers)
    assert denied.status_code == 403
    history = client.get(
        "/api/v1/clothing/customer-history",
        headers=headers,
        query_string={"customer_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert history.status_code == 403


def test_clothing_sales_by_brand_size_category(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    shirts = _category(client, headers, "Shirts")
    pants = _category(client, headers, "Pants")
    tee = _item(client, headers, shirts, "Report Tee", price="200")
    jean = _item(client, headers, pants, "Report Jean", price="300")
    nike_m = _variant(
        client,
        headers,
        tee["id"],
        size="M",
        color="Black",
        brand="Nike",
        stock_quantity="10",
    )
    adidas_l = _variant(
        client,
        headers,
        jean["id"],
        size="L",
        color="Blue",
        brand="Adidas",
        stock_quantity="10",
    )
    _sell(client, headers, tee["id"], nike_m["id"], "2")
    _sell(client, headers, jean["id"], adidas_l["id"], "1")

    report = client.get("/api/v1/clothing/sales", headers=headers)
    assert report.status_code == 200, report.get_json()
    data = report.get_json()["data"]
    brands = {row["brand"]: row for row in data["by_brand"]}
    assert brands["Nike"]["quantity"] == 2.0
    assert brands["Nike"]["revenue"] == 400.0
    assert brands["Adidas"]["quantity"] == 1.0
    assert brands["Adidas"]["revenue"] == 300.0

    sizes = {row["size"]: row for row in data["by_size"]}
    assert sizes["M"]["revenue"] == 400.0
    assert sizes["L"]["revenue"] == 300.0

    cats = {row["category_name"]: row for row in data["by_category"]}
    assert cats["Shirts"]["revenue"] == 400.0
    assert cats["Pants"]["revenue"] == 300.0

    nike_only = client.get(
        "/api/v1/clothing/sales",
        headers=headers,
        query_string={"brand": "Nike"},
    )
    assert nike_only.status_code == 200, nike_only.get_json()
    nike_data = nike_only.get_json()["data"]
    assert [row["brand"] for row in nike_data["by_brand"]] == ["Nike"]
    assert nike_data["by_brand"][0]["revenue"] == 400.0

    stock_ids = {row["variant_id"] for row in data["variant_stock"]}
    assert nike_m["id"] in stock_ids
    assert adidas_l["id"] in stock_ids


def test_clothing_report_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_clothing(client, owner_a)
    cat_id = _category(client, owner_a, "Iso Wear")
    item = _item(client, owner_a, cat_id, "Iso Tee")
    variant = _variant(
        client,
        owner_a,
        item["id"],
        size="S",
        color="Red",
        brand="SecretBrand",
        stock_quantity="5",
    )
    _sell(client, owner_a, item["id"], variant["id"], "1")

    assert client.get("/api/v1/clothing/sales", headers=owner_b).status_code == 403
    _switch_clothing(client, owner_b)
    other = client.get("/api/v1/clothing/sales", headers=owner_b)
    assert other.status_code == 200, other.get_json()
    brands = {row["brand"] for row in other.get_json()["data"]["by_brand"]}
    assert "SecretBrand" not in brands


def test_clothing_customer_history_includes_variant_lines(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers, "History Wear")
    item = _item(client, headers, cat_id, "History Tee")
    variant = _variant(
        client,
        headers,
        item["id"],
        size="M",
        color="Green",
        brand="House",
        stock_quantity="4",
    )
    customer = _customer(client, headers, "Walk-in Shopper", "9876280101")
    bill = _sell(client, headers, item["id"], variant["id"], "1", customer_id=customer["id"])

    missing = client.get("/api/v1/clothing/customer-history", headers=headers)
    assert missing.status_code == 400

    history = client.get(
        "/api/v1/clothing/customer-history",
        headers=headers,
        query_string={"customer_id": customer["id"]},
    )
    assert history.status_code == 200, history.get_json()
    data = history.get_json()["data"]
    assert data["customer"]["id"] == customer["id"]
    assert data["bills"][0]["id"] == bill["id"]
    assert data["bills"][0]["items"][0]["variant_id"] == variant["id"]


def test_gate_clothing_cross_tenant_isolation_matrix(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_clothing(client, owner_a)
    cat_id = _category(client, owner_a, "Gate-Cloth-Iso")
    item = _item(client, owner_a, cat_id, "Gate Iso Shirt")
    variant = _variant(
        client,
        owner_a,
        item["id"],
        size="M",
        color="Navy",
        brand="GateBrand",
        barcode="8902800000001",
        stock_quantity="6",
    )
    customer = _customer(client, owner_a, "Gate Iso Buyer", "9876280201")
    bill = _sell(client, owner_a, item["id"], variant["id"], "1", customer_id=customer["id"])

    restaurant_probes = [
        "/api/v1/clothing/pos-catalog",
        "/api/v1/clothing/sales",
        "/api/v1/returns",
        f"/api/v1/items/{item['id']}/variants",
        f"/api/v1/items/{item['id']}/images",
    ]
    for path in restaurant_probes:
        response = client.get(path, headers=owner_b)
        assert response.status_code == 403, (path, response.get_json())

    _switch_clothing(client, owner_b)
    hidden = [
        f"/api/v1/items/{item['id']}/variants",
        "/api/v1/items/by-barcode/8902800000001",
        f"/api/v1/clothing/customer-history?customer_id={customer['id']}",
        f"/api/v1/returns/lookup?bill_number={bill['bill_number']}",
    ]
    for path in hidden:
        response = client.get(path, headers=owner_b)
        assert response.status_code == 404, (path, response.get_json())

    catalog_b = client.get("/api/v1/clothing/pos-catalog", headers=owner_b).get_json()["data"]
    ids = {row["id"] for row in catalog_b["items"]}
    assert item["id"] not in ids


def test_gate_clothing_permission_matrix(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_clothing(client, owner)

    assert client.get("/api/v1/clothing/pos-catalog", headers=billing).status_code == 200
    assert client.get("/api/v1/clothing/sales", headers=manager).status_code == 200
    assert client.get("/api/v1/clothing/sales", headers=billing).status_code == 403
    assert client.post("/api/v1/returns", headers=billing, json={}).status_code == 403
    assert client.get("/api/v1/returns", headers=billing).status_code == 200


def test_gate_clothing_module_matrix(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, owner)
    clothing = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in ("variants", "product_images", "returns_exchange", "barcode_pos"):
        assert code in clothing
    assert "customer_credit" not in clothing
    assert "order_channels" not in clothing

    resto = login(client, "owner@hotelb.com", "Owner@12345")
    resto_modules = client.get("/api/v1/tenants/me/modules", headers=resto).get_json()["data"][
        "enabled_modules"
    ]
    assert "variants" not in resto_modules
    assert "returns_exchange" not in resto_modules


def test_gate_clothing_return_stock_and_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, owner)
    cat_id = _category(client, owner, "Gate-Cloth-Audit")
    item = _item(client, owner, cat_id, "Gate Audit Tee")
    medium = _variant(
        client,
        owner,
        item["id"],
        size="M",
        color="Black",
        brand="AuditBrand",
        stock_quantity="4",
    )
    _variant(
        client,
        owner,
        item["id"],
        size="L",
        color="Black",
        brand="AuditBrand",
        stock_quantity="4",
    )
    customer = _customer(client, owner, "Gate Audit Buyer", "9876280301")
    bill = _sell(client, owner, item["id"], medium["id"], "2", customer_id=customer["id"])
    created = client.post(
        "/api/v1/returns",
        headers=owner,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Gate return",
            "items": [{"bill_item_id": bill["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()

    stocks = {
        row["id"]: float(row["stock_quantity"])
        for row in client.get(f"/api/v1/items/{item['id']}/variants", headers=owner).get_json()[
            "data"
        ]
    }
    assert stocks[medium["id"]] == 3.0

    sales = client.get("/api/v1/clothing/sales", headers=owner)
    assert sales.status_code == 200, sales.get_json()
    assert sales.get_json()["data"]["returns"]["return_count"] >= 1
    assert sales.get_json()["data"]["returns"]["refund_amount"] >= 200.0

    actions = set(_audit_actions(client, owner))
    assert "CREATE_VARIANT" in actions
    assert "CREATE_RETURN" in actions
    assert "VIEW_CLOTHING_REPORT" in actions


def test_gate_clothing_api_response_contracts(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, owner)
    customer = _customer(client, owner, "Gate Contract Buyer", "9876280401")

    list_endpoints = [
        "/api/v1/clothing/pos-catalog",
        "/api/v1/clothing/sales",
        "/api/v1/returns",
        "/api/v1/item-variants",
    ]
    for path in list_endpoints:
        response = client.get(path, headers=owner)
        assert response.status_code == 200, (path, response.get_json())
        body = response.get_json()
        assert body["success"] is True
        assert "data" in body

    sales = client.get("/api/v1/clothing/sales", headers=owner).get_json()["data"]
    for key in ("by_brand", "by_size", "by_color", "by_category", "variant_stock", "returns", "metrics"):
        assert key in sales

    history = client.get(
        "/api/v1/clothing/customer-history",
        headers=owner,
        query_string={"customer_id": customer["id"]},
    )
    assert history.status_code == 200, history.get_json()
    assert history.get_json()["success"] is True
    assert "bills" in history.get_json()["data"]


def test_gate_manager_clothing_ops_path(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch_clothing(client, owner)
    cat_id = _category(client, owner, "Gate-Cloth-Mgr")
    item = _item(client, owner, cat_id, "Gate Mgr Shirt")
    variant = _variant(
        client, owner, item["id"], size="M", color="White", brand="Mgr", stock_quantity="5"
    )
    bill = _sell(client, manager, item["id"], variant["id"], "1")
    returned = client.post(
        "/api/v1/returns",
        headers=manager,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Manager return",
            "items": [{"bill_item_id": bill["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert returned.status_code == 201, returned.get_json()
    assert client.get("/api/v1/clothing/sales", headers=manager).status_code == 200
