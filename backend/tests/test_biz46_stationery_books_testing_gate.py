"""Sprint BIZ-46 — stationery / books testing gate.

Regression matrix across BIZ-44 … BIZ-45: stationery POS + credit, book
metadata/search, book returns/exchanges, module matrix, isolation,
permissions, audit, and API contracts.

Run full phase gate from backend/:
  python -m pytest tests/test_biz44_stationery_pack.py \\
    tests/test_biz45_book_store_metadata.py \\
    tests/test_biz46_stationery_books_testing_gate.py -q
"""

from tests.conftest import login


def _switch(client, headers, business_type: str):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Gate Cat"):
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


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_restaurant_phase08_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    for path in (
        "/api/v1/stationery/pos-catalog",
        "/api/v1/books/catalog",
        "/api/v1/returns",
    ):
        assert client.get(path, headers=owner).status_code == 403, path


def test_gate_module_matrix_stationery(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "stationery")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in ("barcode_pos", "bulk_pricing", "customer_credit"):
        assert code in modules, code
    assert "returns_exchange" not in modules
    assert "book_metadata" not in modules
    assert "serial_imei" not in modules


def test_gate_module_matrix_book_store(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "book_store")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in ("book_metadata", "barcode_pos", "bulk_pricing", "returns_exchange"):
        assert code in modules, code
    assert "serial_imei" not in modules
    assert "production" not in modules


def test_gate_stationery_pos_and_credit_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "stationery")
    cat_id = _category(client, owner, "Gate-Stat")
    pen = _item(
        client,
        owner,
        cat_id,
        "Gate Pen",
        barcode="8908111999001",
        price="10",
        stock_quantity="30",
    )
    customer = client.post(
        "/api/v1/customers",
        headers=owner,
        json={"name": "Gate School", "phone_country_code": "91", "phone": "9000000046"},
    ).get_json()["data"]

    catalog = client.get("/api/v1/stationery/pos-catalog", headers=billing)
    assert catalog.status_code == 200, catalog.get_json()
    assert catalog.get_json()["success"] is True

    credit = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "credit",
            "customer_id": customer["id"],
            "items": [{"item_id": pen["id"], "quantity": "2"}],
        },
    )
    assert credit.status_code == 201, credit.get_json()
    stock = client.get(f"/api/v1/items/{pen['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 28.0


def test_gate_book_isbn_search_and_sell(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "book_store")
    cat_id = _category(client, owner, "Gate-Books")
    book = _item(
        client,
        owner,
        cat_id,
        "Gate Odyssey",
        isbn="9780140449136",
        author="Homer",
        publisher="Penguin",
        price="250",
        stock_quantity="5",
    )

    found = client.get("/api/v1/books/by-isbn/978-0140449136", headers=billing)
    assert found.status_code == 200, found.get_json()
    assert found.get_json()["data"]["id"] == book["id"]

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": book["id"], "quantity": "2"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    stock = client.get(f"/api/v1/items/{book['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 3.0


def test_gate_book_return_restocks_and_refund(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "book_store")
    cat_id = _category(client, owner, "Gate-Ret")
    book = _item(
        client,
        owner,
        cat_id,
        "Gate Return Title",
        isbn="9780141439518",
        author="Austen",
        price="200",
        stock_quantity="10",
    )
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": book["id"], "quantity": "2"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_data = bill.get_json()["data"]

    created = client.post(
        "/api/v1/returns",
        headers=owner,
        json={
            "bill_id": bill_data["id"],
            "kind": "RETURN",
            "reason": "Damaged pages",
            "items": [{"bill_item_id": bill_data["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["kind"] == "RETURN"
    assert float(body["refund_amount"]) == 200.0

    stock = client.get(f"/api/v1/items/{book['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 9.0  # 10 - 2 + 1
    assert "CREATE_RETURN" in _audit_actions(client, owner, action="CREATE_RETURN")


def test_gate_book_exchange_title_for_title(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "book_store")
    cat_id = _category(client, owner, "Gate-Ex")
    sold = _item(
        client,
        owner,
        cat_id,
        "Gate Sold Book",
        isbn="9780007117116",
        price="150",
        stock_quantity="4",
    )
    swap = _item(
        client,
        owner,
        cat_id,
        "Gate Swap Book",
        isbn="9780007117117",
        price="150",
        stock_quantity="6",
    )
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": sold["id"], "quantity": "1"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_data = bill.get_json()["data"]

    swapped = client.post(
        "/api/v1/returns",
        headers=owner,
        json={
            "bill_id": bill_data["id"],
            "kind": "EXCHANGE",
            "reason": "Wrong title",
            "items": [
                {
                    "bill_item_id": bill_data["items"][0]["id"],
                    "quantity": "1",
                    "exchange_item_id": swap["id"],
                }
            ],
        },
    )
    assert swapped.status_code == 201, swapped.get_json()
    assert swapped.get_json()["data"]["kind"] == "EXCHANGE"

    sold_stock = client.get(f"/api/v1/items/{sold['id']}", headers=owner).get_json()["data"]
    swap_stock = client.get(f"/api/v1/items/{swap['id']}", headers=owner).get_json()["data"]
    assert sold_stock["stock_quantity"] == 4.0  # 4 - 1 + 1
    assert swap_stock["stock_quantity"] == 5.0  # 6 - 1
    assert "CREATE_EXCHANGE" in _audit_actions(client, owner, action="CREATE_EXCHANGE")


def test_gate_book_return_permissions(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "book_store")
    cat_id = _category(client, owner, "Gate-Perm")
    book = _item(client, owner, cat_id, "Gate Perm Book", price="80", stock_quantity="5")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": book["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    listed = client.get("/api/v1/returns", headers=billing)
    assert listed.status_code == 200, listed.get_json()

    denied = client.post(
        "/api/v1/returns",
        headers=billing,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Billing cannot write",
            "items": [{"bill_item_id": bill["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert denied.status_code == 403, denied.get_json()

    ok = client.post(
        "/api/v1/returns",
        headers=manager,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Manager OK",
            "items": [{"bill_item_id": bill["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert ok.status_code == 201, ok.get_json()
    assert ok.get_json()["success"] is True


def test_gate_stationery_returns_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "stationery")
    assert client.get("/api/v1/returns", headers=owner).status_code == 403


def test_gate_cross_tenant_book_return_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    billing_a = login(client, "billing@hotela.com", "Billing@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "book_store")
    _switch(client, owner_b, "book_store")

    cat_id = _category(client, owner_a, "Gate-Iso")
    book = _item(client, owner_a, cat_id, "Gate Iso Book", price="90", stock_quantity="3")
    bill = client.post(
        "/api/v1/bills",
        headers=billing_a,
        json={
            "payment_method": "cash",
            "items": [{"item_id": book["id"], "quantity": "1"}],
        },
    ).get_json()["data"]
    ret = client.post(
        "/api/v1/returns",
        headers=owner_a,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Isolation",
            "items": [{"bill_item_id": bill["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert ret.status_code == 201, ret.get_json()
    return_id = ret.get_json()["data"]["id"]

    denied = client.get(f"/api/v1/returns/{return_id}", headers=owner_b)
    assert denied.status_code in (403, 404), denied.get_json()


def test_gate_api_envelopes(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "book_store")
    catalog = client.get("/api/v1/books/catalog", headers=owner)
    assert catalog.status_code == 200, catalog.get_json()
    assert catalog.get_json()["success"] is True
    assert "data" in catalog.get_json()

    _switch(client, owner, "stationery")
    pos = client.get("/api/v1/stationery/pos-catalog", headers=owner)
    assert pos.status_code == 200, pos.get_json()
    assert pos.get_json()["success"] is True
