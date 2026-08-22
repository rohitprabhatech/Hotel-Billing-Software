"""Sprint BIZ-10 — common platform readiness regression gate.

Integration, isolation, permission, audit, and contract checks across BIZ-01…BIZ-09.
Run with: pytest tests/test_biz10_platform_readiness_gate.py -q
Full phase gate: pytest tests/test_biz01_business_types.py tests/test_biz02_modules.py
  tests/test_biz03_manager.py tests/test_biz04_customers.py tests/test_biz05_suppliers.py
  tests/test_biz06_purchases.py tests/test_biz07_expenses.py tests/test_biz08_barcode_uom.py
  tests/test_biz09_party_ledger.py tests/test_biz10_platform_readiness_gate.py -q
"""

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, stock="20", barcode=None):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "120",
        "gst_percentage": "5",
        "stock_quantity": stock,
        "uom": "pcs",
    }
    if barcode:
        payload["barcode"] = barcode
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


def _supplier(client, headers, name, phone):
    response = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": phone},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _audit_actions(client, headers, *, action=None, entity_type=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    if entity_type:
        params["entity_type"] = entity_type
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_gate_common_modules_cross_tenant_isolation(client):
    """BIZ-04…09 resources must not leak across tenants."""
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    cat_a = _category(client, owner_a, "Gate-A-Cat")
    item_a = _item(client, owner_a, cat_a, "Gate-A-Item", barcode="8909000000001")
    customer_a = _customer(client, owner_a, "Gate A Customer", "9876600101")
    supplier_a = _supplier(client, owner_a, "Gate A Supplier", "9876600102")

    purchase_a = client.post(
        "/api/v1/purchases",
        headers=owner_a,
        json={
            "supplier_id": supplier_a["id"],
            "items": [{"item_id": item_a["id"], "quantity": "2", "unit_cost": "40"}],
        },
    )
    assert purchase_a.status_code == 201, purchase_a.get_json()
    purchase_id = purchase_a.get_json()["data"]["id"]

    expense_a = client.post(
        "/api/v1/expenses",
        headers=owner_a,
        json={"category": "Rent", "amount": "500", "expense_date": "2026-08-01"},
    )
    assert expense_a.status_code == 201, expense_a.get_json()
    expense_id = expense_a.get_json()["data"]["id"]

    credit_bill = client.post(
        "/api/v1/bills",
        headers=owner_a,
        json={
            "payment_method": "credit",
            "customer_id": customer_a["id"],
            "items": [{"item_id": item_a["id"], "quantity": "1"}],
        },
    )
    assert credit_bill.status_code == 201, credit_bill.get_json()

    probes = [
        f"/api/v1/customers/{customer_a['id']}",
        f"/api/v1/suppliers/{supplier_a['id']}",
        f"/api/v1/purchases/{purchase_id}",
        f"/api/v1/expenses/{expense_id}",
        f"/api/v1/customers/{customer_a['id']}/ledger",
        "/api/v1/items/by-barcode/8909000000001",
    ]
    for path in probes:
        response = client.get(path, headers=owner_b)
        assert response.status_code == 404, (path, response.get_json())

    list_a = client.get("/api/v1/customers/outstanding", headers=owner_a).get_json()["data"]
    list_b = client.get("/api/v1/customers/outstanding", headers=owner_b).get_json()["data"]
    assert any(row["id"] == customer_a["id"] for row in list_a)
    assert all(row["id"] != customer_a["id"] for row in list_b)


def test_gate_procurement_to_billing_stock_interaction(client):
    """Purchase increases stock; billing deducts; movements ledger reflects both."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, owner, "Gate-Stock-Cat")
    item = _item(client, owner, cat_id, "Gate Stock Item", stock="5")
    supplier = _supplier(client, owner, "Gate Stock Supplier", "9876600201")

    purchase = client.post(
        "/api/v1/purchases",
        headers=owner,
        json={
            "supplier_id": supplier["id"],
            "items": [{"item_id": item["id"], "quantity": "10", "unit_cost": "30"}],
        },
    )
    assert purchase.status_code == 201, purchase.get_json()

    after_purchase = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert after_purchase["stock_quantity"] == 15.0

    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": "3"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()

    after_bill = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert after_bill["stock_quantity"] == 12.0

    movements = client.get(
        "/api/v1/stock-movements",
        headers=owner,
        query_string={"item_id": item["id"]},
    ).get_json()["data"]
    sources = {row["source"] for row in movements}
    assert "PURCHASE" in sources
    assert "BILL" in sources


def test_gate_credit_sale_collection_and_outstanding(client):
    """Credit bill → balance → full payment → outstanding list updates."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, owner, "Gate-Credit-Cat")
    item = _item(client, owner, cat_id, "Gate Credit Item", stock="50")
    customer = _customer(client, owner, "Gate Credit Customer", "9876600301")

    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": item["id"], "quantity": "2"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    total = bill.get_json()["data"]["grand_total"]

    detail = client.get(f"/api/v1/customers/{customer['id']}", headers=owner).get_json()["data"]
    assert detail["balance"] == total

    pay = client.post(
        f"/api/v1/customers/{customer['id']}/payments",
        headers=owner,
        json={"amount": str(total), "collection_method": "cash"},
    )
    assert pay.status_code == 201, pay.get_json()

    cleared = client.get(f"/api/v1/customers/{customer['id']}", headers=owner).get_json()["data"]
    assert cleared["balance"] == 0

    outstanding = client.get("/api/v1/customers/outstanding", headers=owner).get_json()["data"]
    assert all(row["id"] != customer["id"] for row in outstanding)


def test_gate_permission_matrix_common_modules(client):
    """Role boundaries for new common modules."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    assert client.get("/api/v1/purchases", headers=owner).status_code == 200
    assert client.get("/api/v1/purchases", headers=manager).status_code == 200
    assert client.get("/api/v1/purchases", headers=billing).status_code == 403

    assert client.get("/api/v1/expenses", headers=owner).status_code == 200
    assert client.get("/api/v1/expenses", headers=manager).status_code == 200
    assert client.get("/api/v1/expenses", headers=billing).status_code == 403

    assert client.get("/api/v1/suppliers", headers=billing).status_code == 200
    assert client.get("/api/v1/customers", headers=billing).status_code == 200

    assert client.get("/api/v1/users", headers=manager).status_code == 403
    assert client.get("/api/v1/audit-logs", headers=manager).status_code == 403
    assert client.get("/api/v1/reports/summary", headers=billing).status_code == 403


def test_gate_audit_trail_for_common_module_mutations(client):
    """Owner audit log captures CRM, procurement, and expense actions."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, owner, "Gate-Audit-Cat")
    item = _item(client, owner, cat_id, "Gate Audit Item")
    customer = _customer(client, owner, "Gate Audit Customer", "9876600401")
    _supplier(client, owner, "Gate Audit Supplier", "9876600402")

    client.post(
        "/api/v1/purchases",
        headers=owner,
        json={"items": [{"item_id": item["id"], "quantity": "1", "unit_cost": "10"}]},
    )
    client.post(
        "/api/v1/expenses",
        headers=owner,
        json={"category": "Utilities", "amount": "99", "expense_date": "2026-08-02"},
    )
    client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )

    actions = set(_audit_actions(client, owner))
    assert "CREATE_CUSTOMER" in actions
    assert "CREATE_SUPPLIER" in actions
    assert "CREATE_PURCHASE" in actions
    assert "CREATE_EXPENSE" in actions
    assert "CREDIT_SALE" in actions


def test_gate_api_response_contracts(client):
    """Standard success envelope on common module list endpoints."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    list_endpoints = [
        "/api/v1/customers",
        "/api/v1/suppliers",
        "/api/v1/purchases",
        "/api/v1/expenses",
        "/api/v1/customers/outstanding",
    ]
    for path in list_endpoints:
        response = client.get(path, headers=owner)
        assert response.status_code == 200, (path, response.get_json())
        body = response.get_json()
        assert body["success"] is True
        assert "data" in body
        assert "meta" in body
        assert isinstance(body["data"], list)

    modules = client.get("/api/v1/tenants/me/modules", headers=owner)
    assert modules.status_code == 200, modules.get_json()
    modules_body = modules.get_json()
    assert modules_body["success"] is True
    assert "enabled_modules" in modules_body["data"]
    assert isinstance(modules_body["data"]["enabled_modules"], list)


def test_gate_manager_end_to_end_ops_path(client):
    """Manager can run daily ops across CRM, procurement, expenses, and reports."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    cat_id = _category(client, owner, "Gate-Mgr-Cat")
    item = _item(client, owner, cat_id, "Gate Mgr Item", stock="8")

    customer = client.post(
        "/api/v1/customers",
        headers=manager,
        json={"name": "Mgr Customer", "phone_country_code": "91", "phone": "9876600501"},
    )
    assert customer.status_code == 201, customer.get_json()

    expense = client.post(
        "/api/v1/expenses",
        headers=manager,
        json={"category": "Transport", "amount": "75", "expense_date": "2026-08-03"},
    )
    assert expense.status_code == 201, expense.get_json()

    purchase = client.post(
        "/api/v1/purchases",
        headers=manager,
        json={"items": [{"item_id": item["id"], "quantity": "2", "unit_cost": "25"}]},
    )
    assert purchase.status_code == 201, purchase.get_json()

    report = client.get("/api/v1/reports/summary", headers=manager)
    assert report.status_code == 200, report.get_json()


def test_gate_business_types_and_modules_smoke(client):
    """BIZ-01/BIZ-02 baseline still reachable."""
    response = client.get("/api/v1/tenants/business-types")
    assert response.status_code == 200
    types = response.get_json()["data"]["business_types"]
    assert len(types) == 14

    owner = login(client, "owner@hotela.com", "Owner@12345")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner)
    assert modules.status_code == 200
    enabled = modules.get_json()["data"]["enabled_modules"]
    assert "core_billing" in enabled
