"""Sprint BIZ-09 — party ledger / customer credit."""

from tests.conftest import login


def _create_category(client, headers, name="Credit Category"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _create_item(client, headers, category_id, name="Credit Item"):
    response = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": name,
            "category_id": category_id,
            "price": "200",
            "gst_percentage": "5",
            "stock_quantity": "100",
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _create_customer(client, headers, name="Credit Customer", phone="9876512345", credit_limit=None):
    payload = {
        "name": name,
        "phone_country_code": "91",
        "phone": phone,
    }
    if credit_limit is not None:
        payload["credit_limit"] = credit_limit
    response = client.post("/api/v1/customers", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _credit_bill(client, headers, item_id, customer_id, quantity="1"):
    response = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "items": [{"item_id": item_id, "quantity": quantity}],
            "payment_method": "credit",
            "customer_id": customer_id,
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_credit_bill_increases_customer_balance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id)
    customer = _create_customer(client, owner, phone="9876511111")

    bill = _credit_bill(client, owner, item["id"], customer["id"])
    assert bill["payment_method"] == "credit"

    detail = client.get(f"/api/v1/customers/{customer['id']}", headers=owner)
    assert detail.status_code == 200, detail.get_json()
    assert detail.get_json()["data"]["balance"] == bill["grand_total"]

    ledger = client.get(f"/api/v1/customers/{customer['id']}/ledger", headers=owner)
    assert ledger.status_code == 200, ledger.get_json()
    body = ledger.get_json()["data"]
    assert body["balance"] == bill["grand_total"]
    assert any(row["entry_type"] == "CREDIT_SALE" for row in body["entries"])


def test_payment_decreases_balance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id)
    customer = _create_customer(client, owner, name="Pay Customer", phone="9876522222")
    bill = _credit_bill(client, owner, item["id"], customer["id"])

    payment = client.post(
        f"/api/v1/customers/{customer['id']}/payments",
        headers=owner,
        json={"amount": "100", "collection_method": "cash", "notes": "Partial"},
    )
    assert payment.status_code == 201, payment.get_json()
    assert payment.get_json()["data"]["entry_type"] == "PAYMENT"

    detail = client.get(f"/api/v1/customers/{customer['id']}", headers=owner)
    expected = bill["grand_total"] - 100
    assert detail.get_json()["data"]["balance"] == expected


def test_overpayment_rejected(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id)
    customer = _create_customer(client, owner, name="Overpay Customer", phone="9876533333")
    _credit_bill(client, owner, item["id"], customer["id"])

    blocked = client.post(
        f"/api/v1/customers/{customer['id']}/payments",
        headers=owner,
        json={"amount": "99999"},
    )
    assert blocked.status_code == 400, blocked.get_json()


def test_credit_limit_enforced(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id, name="Limit Item")
    customer = _create_customer(
        client, owner, name="Limit Customer", phone="9876544444", credit_limit="150"
    )

    blocked = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )
    assert blocked.status_code == 400, blocked.get_json()


def test_cancel_credit_bill_reverses_balance(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id)
    customer = _create_customer(client, owner, name="Cancel Customer", phone="9876555555")
    bill = _credit_bill(client, owner, item["id"], customer["id"])

    cancelled = client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=owner,
        json={"reason": "Wrong customer"},
    )
    assert cancelled.status_code == 200, cancelled.get_json()

    detail = client.get(f"/api/v1/customers/{customer['id']}", headers=owner)
    assert detail.get_json()["data"]["balance"] == 0


def test_outstanding_list(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id)
    customer = _create_customer(client, owner, name="Outstanding Customer", phone="9876566666")
    _credit_bill(client, owner, item["id"], customer["id"])

    outstanding = client.get("/api/v1/customers/outstanding", headers=owner)
    assert outstanding.status_code == 200, outstanding.get_json()
    rows = outstanding.get_json()["data"]
    assert any(row["id"] == customer["id"] and row["balance"] > 0 for row in rows)


def test_credit_bill_requires_customer(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id)

    blocked = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
        },
    )
    assert blocked.status_code == 400, blocked.get_json()


def test_ledger_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    category_id = _create_category(client, owner_a)
    item = _create_item(client, owner_a, category_id)
    customer = _create_customer(client, owner_a, name="Tenant A Credit", phone="9876577777")
    _credit_bill(client, owner_a, item["id"], customer["id"])

    denied = client.get(f"/api/v1/customers/{customer['id']}/ledger", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_billing_user_can_collect_payment(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id)
    customer = _create_customer(client, owner, name="Billing Collect", phone="9876588888")
    _credit_bill(client, owner, item["id"], customer["id"])

    payment = client.post(
        f"/api/v1/customers/{customer['id']}/payments",
        headers=billing,
        json={"amount": "50", "collection_method": "cash"},
    )
    assert payment.status_code == 201, payment.get_json()
