"""Sprint BIZ-37 — transport charges + supplier/customer trade credit."""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Trade"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name="Cement Bag", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "18",
        "stock_quantity": "200",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _customer(client, headers, name="Builder"):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "+91", "phone": "9876543210"},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _supplier(client, headers, name="Steel Depot"):
    response = client.post("/api/v1/suppliers", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_bill_totals_include_transport_non_gst(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, price="100", gst_percentage="18")

    # 1 x 100 = 100 taxable; GST 18; transport 50 non-GST → pre-round 168 → grand 168
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "cash",
            "transport_charge": "50",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    data = bill.get_json()["data"]
    assert Decimal(str(data["taxable_amount"])) == Decimal("100.00")
    assert Decimal(str(data["gst_amount"])) == Decimal("18.00")
    assert Decimal(str(data["transport_charge"])) == Decimal("50.00")
    assert Decimal(str(data["grand_total"])) == Decimal("168")


def test_credit_sale_outstanding_includes_transport(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, price="100", gst_percentage="0")
    customer = _customer(client, owner)

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "2"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
            "transport_charge": "25",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert Decimal(str(bill.get_json()["data"]["grand_total"])) == Decimal("225")

    outstanding = client.get("/api/v1/customers/outstanding", headers=owner)
    assert outstanding.status_code == 200, outstanding.get_json()
    rows = outstanding.get_json()["data"]
    match = next(row for row in rows if row["id"] == customer["id"])
    assert Decimal(str(match["balance"])) == Decimal("225.00")


def test_challan_convert_carries_transport(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner, "Pipe")
    item = _item(client, owner, cat_id, price="450", gst_percentage="0", uom="m")

    challan = client.post(
        "/api/v1/challans",
        headers=owner,
        json={
            "customer_name": "Site",
            "transport_charge": "100",
            "items": [{"item_id": item["id"], "quantity": "10"}],
        },
    )
    assert challan.status_code == 201, challan.get_json()
    body = challan.get_json()["data"]
    assert Decimal(str(body["transport_charge"])) == Decimal("100.00")

    converted = client.post(
        f"/api/v1/challans/{body['id']}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted.status_code == 200, converted.get_json()
    bill = converted.get_json()["data"]["bill"]
    assert Decimal(str(bill["transport_charge"])) == Decimal("100.00")
    assert Decimal(str(bill["grand_total"])) == Decimal("4600")  # 4500 + 100


def test_supplier_credit_purchase_and_payment(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, stock_quantity="10")
    supplier = _supplier(client, owner)

    purchase = client.post(
        "/api/v1/purchases",
        headers=owner,
        json={
            "supplier_id": supplier["id"],
            "payment_method": "credit",
            "items": [{"item_id": item["id"], "quantity": "5", "unit_cost": "40"}],
        },
    )
    assert purchase.status_code == 201, purchase.get_json()
    assert Decimal(str(purchase.get_json()["data"]["total_amount"])) == Decimal("200.00")

    outstanding = client.get("/api/v1/suppliers/outstanding", headers=owner)
    assert outstanding.status_code == 200, outstanding.get_json()
    rows = outstanding.get_json()["data"]
    match = next(row for row in rows if row["id"] == supplier["id"])
    assert Decimal(str(match["balance"])) == Decimal("200.00")

    paid = client.post(
        f"/api/v1/suppliers/{supplier['id']}/payments",
        headers=owner,
        json={"amount": "75", "collection_method": "cash"},
    )
    assert paid.status_code == 201, paid.get_json()

    ledger = client.get(f"/api/v1/suppliers/{supplier['id']}/ledger", headers=owner)
    assert ledger.status_code == 200, ledger.get_json()
    assert Decimal(str(ledger.get_json()["data"]["balance"])) == Decimal("125.00")


def test_grocery_rejects_transport_charge(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "grocery_kirana")
    cat_id = _category(client, owner, "Kirana")
    item = _item(client, owner, cat_id)

    denied = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "cash",
            "transport_charge": "10",
        },
    )
    assert denied.status_code == 400, denied.get_json()
