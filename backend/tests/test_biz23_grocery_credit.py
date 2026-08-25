"""Sprint BIZ-23 — grocery credit (udhari) and sales reports."""

from tests.conftest import login


def _switch_grocery(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "grocery_kirana"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Kirana Cat"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "20",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _customer(client, headers, name="Udhari Customer", phone="9876590001"):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": name,
            "phone_country_code": "91",
            "phone": phone,
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_grocery_has_customer_credit_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    modules = client.get("/api/v1/tenants/me/modules", headers=headers)
    enabled = modules.get_json()["data"]["enabled_modules"]
    assert "customer_credit" in enabled
    assert "barcode_pos" in enabled


def test_grocery_credit_forbidden_for_restaurant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    denied = client.get("/api/v1/grocery/outstanding", headers=headers)
    assert denied.status_code == 403, denied.get_json()


def test_credit_sale_updates_ledger_and_stock(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, "Atta", stock_quantity="10")
    customer = _customer(client, owner, phone="9876590101")

    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [{"item_id": item["id"], "quantity": "2"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    body = bill.get_json()["data"]
    assert body["payment_method"] == "credit"

    stock = client.get(f"/api/v1/items/{item['id']}", headers=owner)
    assert float(stock.get_json()["data"]["stock_quantity"]) == 8.0

    ledger = client.get(f"/api/v1/grocery/credit/{customer['id']}", headers=owner)
    assert ledger.status_code == 200, ledger.get_json()
    credit = ledger.get_json()["data"]
    assert credit["balance"] == body["grand_total"]
    assert any(row["entry_type"] == "CREDIT_SALE" for row in credit["entries"])


def test_insufficient_stock_blocks_credit_without_ledger(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, "Sugar", stock_quantity="1")
    customer = _customer(client, owner, name="Blocked Credit", phone="9876590102")

    blocked = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [{"item_id": item["id"], "quantity": "5"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )
    assert blocked.status_code == 400, blocked.get_json()

    detail = client.get(f"/api/v1/customers/{customer['id']}", headers=owner)
    assert detail.get_json()["data"]["balance"] == 0

    stock = client.get(f"/api/v1/items/{item['id']}", headers=owner)
    assert float(stock.get_json()["data"]["stock_quantity"]) == 1.0


def test_grocery_credit_payment_reduces_balance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, "Oil")
    customer = _customer(client, owner, name="Pay Udhari", phone="9876590103")

    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    grand = bill.get_json()["data"]["grand_total"]

    payment = client.post(
        f"/api/v1/grocery/credit/{customer['id']}/pay",
        headers=owner,
        json={"amount": "40", "collection_method": "cash"},
    )
    assert payment.status_code == 201, payment.get_json()

    ledger = client.get(f"/api/v1/grocery/credit/{customer['id']}", headers=owner)
    assert ledger.get_json()["data"]["balance"] == grand - 40


def test_grocery_outstanding_and_sales_report(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, owner)
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, "Soap")
    customer = _customer(client, owner, name="Outstanding Kirana", phone="9876590104")

    billed = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )
    assert billed.status_code == 201, billed.get_json()
    grand = billed.get_json()["data"]["grand_total"]

    outstanding = client.get("/api/v1/grocery/outstanding", headers=owner)
    assert outstanding.status_code == 200, outstanding.get_json()
    rows = outstanding.get_json()["data"]
    assert any(row["id"] == customer["id"] and row["balance"] == grand for row in rows)

    sales = client.get("/api/v1/grocery/sales", headers=owner)
    assert sales.status_code == 200, sales.get_json()
    data = sales.get_json()["data"]
    assert data["metrics"]["credit_sales"] >= grand
    assert data["metrics"]["credit_bill_count"] >= 1
    assert data["outstanding"]["outstanding_amount"] >= grand
    assert data["outstanding"]["customer_count"] >= 1


def test_grocery_credit_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_grocery(client, owner_a)
    _switch_grocery(client, owner_b)
    cat_id = _category(client, owner_a)
    item = _item(client, owner_a, cat_id, "Tea")
    customer = _customer(client, owner_a, name="Tenant A Udhari", phone="9876590105")
    client.post(
        "/api/v1/bills",
        headers=owner_a,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )

    denied = client.get(f"/api/v1/grocery/credit/{customer['id']}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()
