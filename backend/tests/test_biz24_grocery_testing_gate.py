"""Sprint BIZ-24 — grocery / kirana testing gate.

Isolation, permissions, stock, credit, expiry, bulk pricing, audit, contracts,
and notifications across BIZ-20 … BIZ-23.

Run full phase gate from backend/:
  python -m pytest tests/test_biz20_grocery_fast_pos.py tests/test_biz21_bulk_pricing.py
    tests/test_biz22_batch_expiry.py tests/test_biz23_grocery_credit.py
    tests/test_biz24_grocery_testing_gate.py -q
"""

from datetime import date, timedelta

from tests.conftest import login


def _switch_grocery(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "grocery_kirana"},
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
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "50",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
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


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_gate_grocery_cross_tenant_isolation_matrix(client):
    """POS catalog, barcode, batches, tiers, and grocery credit must not leak."""
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_grocery(client, owner_a)

    cat_id = _category(client, owner_a, "Gate-Groc-Iso")
    item = _item(
        client,
        owner_a,
        cat_id,
        "Gate Iso Milk",
        barcode="8902400000002",
        stock_quantity="0",
        tracks_batches=True,
        block_expired_batches=True,
        uom="pcs",
        price="40",
    )
    customer = _customer(client, owner_a, "Gate Iso Customer", "9876240101")

    client.put(
        f"/api/v1/items/{item['id']}/price-tiers",
        headers=owner_a,
        json={"tiers": [{"min_quantity": "3", "unit_price": "35"}]},
    )
    batch = client.post(
        "/api/v1/batches",
        headers=owner_a,
        json={
            "item_id": item["id"],
            "quantity": "8",
            "expiry_date": (date.today() + timedelta(days=10)).isoformat(),
            "batch_code": "GATE-ISO",
        },
    )
    assert batch.status_code == 201, batch.get_json()

    sellable = _item(
        client,
        owner_a,
        cat_id,
        "Gate Iso Soap",
        barcode="8902400000003",
        stock_quantity="10",
        price="25",
    )
    billed = client.post(
        "/api/v1/bills",
        headers=owner_a,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": sellable["id"], "quantity": "1"}],
        },
    )
    assert billed.status_code == 201, billed.get_json()

    restaurant_probes = [
        "/api/v1/grocery/pos-catalog",
        "/api/v1/grocery/outstanding",
        "/api/v1/grocery/sales",
        "/api/v1/grocery/expiry",
        "/api/v1/batches",
        f"/api/v1/items/{item['id']}/price-tiers",
    ]
    for path in restaurant_probes:
        response = client.get(path, headers=owner_b)
        assert response.status_code == 403, (path, response.get_json())

    _switch_grocery(client, owner_b)
    hidden = [
        f"/api/v1/grocery/credit/{customer['id']}",
        "/api/v1/items/by-barcode/8902400000002",
        f"/api/v1/items/{item['id']}/price-tiers",
    ]
    for path in hidden:
        response = client.get(path, headers=owner_b)
        assert response.status_code == 404, (path, response.get_json())

    batches_b = client.get("/api/v1/batches", headers=owner_b).get_json()["data"]
    assert all(row.get("batch_code") != "GATE-ISO" for row in batches_b)

    catalog_b = client.get("/api/v1/grocery/pos-catalog", headers=owner_b).get_json()["data"]
    ids = {row["id"] for row in catalog_b["items"]}
    assert item["id"] not in ids
    assert sellable["id"] not in ids


def test_gate_kirana_pos_credit_expiry_e2e(client):
    """Barcode + kg sale + bulk tier + udhari + collection + expiry report."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner, "Gate-Groc-E2E")

    rice = _item(
        client,
        owner,
        cat_id,
        "Gate Rice",
        barcode="8902401000001",
        uom="kg",
        price="80",
        stock_quantity="10",
        gst_percentage="0",
    )
    dal = _item(
        client,
        owner,
        cat_id,
        "Gate Dal",
        barcode="8902401000002",
        uom="kg",
        price="120",
        stock_quantity="20",
        gst_percentage="0",
    )
    client.put(
        f"/api/v1/items/{dal['id']}/price-tiers",
        headers=owner,
        json={"tiers": [{"min_quantity": "2", "unit_price": "100"}]},
    )
    milk = _item(
        client,
        owner,
        cat_id,
        "Gate Milk",
        barcode="8902401000003",
        stock_quantity="0",
        tracks_batches=True,
        block_expired_batches=True,
        price="50",
    )
    client.post(
        "/api/v1/batches",
        headers=owner,
        json={
            "item_id": milk["id"],
            "quantity": "6",
            "expiry_date": (date.today() + timedelta(days=2)).isoformat(),
            "batch_code": "GATE-E2E-M",
        },
    )
    customer = _customer(client, owner, "Gate E2E Udhari", "9876240201")

    scanned = client.get("/api/v1/items/by-barcode/8902401000001", headers=owner)
    assert scanned.status_code == 200, scanned.get_json()
    assert scanned.get_json()["data"]["id"] == rice["id"]

    kg_bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "cash",
            "items": [{"item_id": rice["id"], "quantity": "0.5"}],
        },
    )
    assert kg_bill.status_code == 201, kg_bill.get_json()
    assert float(kg_bill.get_json()["data"]["items"][0]["quantity"]) == 0.5
    rice_after = client.get(f"/api/v1/items/{rice['id']}", headers=owner).get_json()["data"]
    assert float(rice_after["stock_quantity"]) == 9.5

    tier_bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "cash",
            "items": [{"item_id": dal["id"], "quantity": "2"}],
        },
    )
    assert tier_bill.status_code == 201, tier_bill.get_json()
    assert float(tier_bill.get_json()["data"]["items"][0]["unit_price"]) == 100.0

    credit_bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": milk["id"], "quantity": "2"}],
        },
    )
    assert credit_bill.status_code == 201, credit_bill.get_json()
    grand = credit_bill.get_json()["data"]["grand_total"]

    ledger = client.get(f"/api/v1/grocery/credit/{customer['id']}", headers=owner).get_json()["data"]
    assert ledger["balance"] == grand

    pay = client.post(
        f"/api/v1/grocery/credit/{customer['id']}/pay",
        headers=owner,
        json={"amount": "20", "collection_method": "cash"},
    )
    assert pay.status_code == 201, pay.get_json()
    after_pay = client.get(f"/api/v1/grocery/credit/{customer['id']}", headers=owner).get_json()["data"]
    assert after_pay["balance"] == grand - 20

    expiry = client.get("/api/v1/grocery/expiry", headers=owner, query_string={"within_days": 7})
    assert expiry.status_code == 200, expiry.get_json()
    assert expiry.get_json()["data"]["summary"]["expiring_count"] >= 1

    sales = client.get("/api/v1/grocery/sales", headers=owner)
    assert sales.status_code == 200, sales.get_json()
    metrics = sales.get_json()["data"]["metrics"]
    assert metrics["credit_sales"] >= grand
    assert sales.get_json()["data"]["outstanding"]["customer_count"] >= 1


def test_gate_grocery_permission_matrix(client):
    """Billing can POS/credit-collect; reports stay owner/manager."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_grocery(client, owner)

    assert client.get("/api/v1/grocery/pos-catalog", headers=owner).status_code == 200
    assert client.get("/api/v1/grocery/pos-catalog", headers=manager).status_code == 200
    assert client.get("/api/v1/grocery/pos-catalog", headers=billing).status_code == 200

    assert client.get("/api/v1/grocery/outstanding", headers=billing).status_code == 200
    assert client.get("/api/v1/grocery/sales", headers=manager).status_code == 200
    assert client.get("/api/v1/grocery/sales", headers=billing).status_code == 403
    assert client.get("/api/v1/batches/expiry", headers=billing).status_code == 200

    resto = login(client, "owner@hotelb.com", "Owner@12345")
    assert client.get("/api/v1/grocery/pos-catalog", headers=resto).status_code == 403


def test_gate_grocery_module_matrix(client):
    """Grocery pack modules vs restaurant vs clothing."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    grocery = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"]["enabled_modules"]
    for code in ("barcode_pos", "bulk_pricing", "batch_expiry", "customer_credit"):
        assert code in grocery
    assert "order_channels" not in grocery
    assert "kot" not in grocery

    resto = login(client, "owner@hotelb.com", "Owner@12345")
    resto_modules = client.get("/api/v1/tenants/me/modules", headers=resto).get_json()["data"]["enabled_modules"]
    assert "barcode_pos" not in resto_modules
    assert "customer_credit" not in resto_modules

    client.put("/api/v1/tenants/me", headers=owner, json={"business_type": "clothing"})
    clothing = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"]["enabled_modules"]
    assert "barcode_pos" in clothing
    assert "customer_credit" not in clothing
    assert "batch_expiry" not in clothing


def test_gate_insufficient_stock_and_expired_batch_block(client):
    """Stock and expired-lot policy block bills; ledger stays untouched."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner, "Gate-Groc-Stock")
    low = _item(client, owner, cat_id, "Gate Low Oil", stock_quantity="1", price="90")
    customer = _customer(client, owner, "Gate Stock Customer", "9876240301")

    blocked = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": low["id"], "quantity": "4"}],
        },
    )
    assert blocked.status_code == 400, blocked.get_json()
    assert blocked.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"
    assert client.get(f"/api/v1/customers/{customer['id']}", headers=owner).get_json()["data"]["balance"] == 0

    yogurt = _item(
        client,
        owner,
        cat_id,
        "Gate Yogurt",
        stock_quantity="0",
        tracks_batches=True,
        block_expired_batches=True,
        price="30",
    )
    client.post(
        "/api/v1/batches",
        headers=owner,
        json={
            "item_id": yogurt["id"],
            "quantity": "5",
            "expiry_date": (date.today() - timedelta(days=1)).isoformat(),
            "batch_code": "GATE-EXP",
        },
    )
    expired_sale = client.post(
        "/api/v1/bills",
        headers=owner,
        json={"payment_method": "cash", "items": [{"item_id": yogurt["id"], "quantity": "1"}]},
    )
    assert expired_sale.status_code == 400, expired_sale.get_json()


def test_gate_grocery_audit_and_notifications(client):
    """Credit sale, batch receive, and low-stock alerts are recorded."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner, "Gate-Groc-Audit")
    item = _item(
        client,
        owner,
        cat_id,
        "Gate Audit Sugar",
        stock_quantity="5",
        minimum_stock_level="4",
        price="20",
    )
    customer = _customer(client, owner, "Gate Audit Udhari", "9876240401")
    billed = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": item["id"], "quantity": "2"}],
        },
    )
    assert billed.status_code == 201, billed.get_json()

    milk = _item(
        client,
        owner,
        cat_id,
        "Gate Audit Milk",
        stock_quantity="0",
        tracks_batches=True,
        price="40",
    )
    batch = client.post(
        "/api/v1/batches",
        headers=owner,
        json={
            "item_id": milk["id"],
            "quantity": "3",
            "expiry_date": (date.today() + timedelta(days=4)).isoformat(),
            "batch_code": "GATE-AUD",
        },
    )
    assert batch.status_code == 201, batch.get_json()

    actions = set(_audit_actions(client, owner))
    assert "CREDIT_SALE" in actions
    assert "CREATE_BATCH" in actions

    notes = client.get("/api/v1/notifications", headers=owner, query_string={"per_page": 100})
    assert notes.status_code == 200, notes.get_json()
    types = {row["type"] for row in notes.get_json()["data"]}
    assert "CREDIT_DUE" in types
    assert "LOW_STOCK" in types
    assert "BATCH_EXPIRING" in types


def test_gate_grocery_api_response_contracts(client):
    """Success envelope on grocery list/report aliases."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)

    list_endpoints = [
        "/api/v1/grocery/pos-catalog",
        "/api/v1/grocery/outstanding",
        "/api/v1/grocery/expiry",
        "/api/v1/batches",
    ]
    for path in list_endpoints:
        response = client.get(path, headers=owner)
        assert response.status_code == 200, (path, response.get_json())
        body = response.get_json()
        assert body["success"] is True
        assert "data" in body

    catalog = client.get("/api/v1/grocery/pos-catalog", headers=owner).get_json()["data"]
    assert "items" in catalog
    assert "scan_defaults" in catalog

    sales = client.get("/api/v1/grocery/sales", headers=owner)
    assert sales.status_code == 200, sales.get_json()
    assert sales.get_json()["success"] is True
    data = sales.get_json()["data"]
    assert "metrics" in data
    assert "outstanding" in data
    assert "credit_sales" in data["metrics"]


def test_gate_manager_grocery_ops_path(client):
    """Manager can bill, receive a batch, collect udhari, and open kirana sales."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner, "Gate-Groc-Mgr")
    item = _item(client, owner, cat_id, "Gate Mgr Biscuit", stock_quantity="12", price="15")
    customer = _customer(client, owner, "Gate Mgr Customer", "9876240501")

    bill = client.post(
        "/api/v1/bills",
        headers=manager,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()

    collect = client.post(
        f"/api/v1/grocery/credit/{customer['id']}/pay",
        headers=manager,
        json={"amount": "5", "collection_method": "cash"},
    )
    assert collect.status_code == 201, collect.get_json()

    milk = _item(
        client,
        owner,
        cat_id,
        "Gate Mgr Milk",
        stock_quantity="0",
        tracks_batches=True,
        price="48",
    )
    received = client.post(
        "/api/v1/batches",
        headers=manager,
        json={
            "item_id": milk["id"],
            "quantity": "4",
            "expiry_date": (date.today() + timedelta(days=12)).isoformat(),
            "batch_code": "GATE-MGR",
        },
    )
    assert received.status_code == 201, received.get_json()

    sales = client.get("/api/v1/grocery/sales", headers=manager)
    assert sales.status_code == 200, sales.get_json()


def test_gate_biz20_through_23_smoke(client):
    """Grocery sprint modules and POS catalog remain reachable."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    modules = client.get("/api/v1/tenants/me/modules", headers=owner)
    assert modules.status_code == 200
    enabled = modules.get_json()["data"]["enabled_modules"]
    assert "barcode_pos" in enabled
    assert "bulk_pricing" in enabled
    assert "batch_expiry" in enabled
    assert "customer_credit" in enabled

    catalog = client.get("/api/v1/grocery/pos-catalog", headers=owner)
    assert catalog.status_code == 200, catalog.get_json()
    assert isinstance(catalog.get_json()["data"]["items"], list)
