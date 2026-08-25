"""Sprint BIZ-27 — clothing returns and exchanges restock variants."""

from tests.conftest import login


def _switch_clothing(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Returns Wear"):
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


def _sell(client, headers, item_id, variant_id, quantity="1"):
    billed = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item_id, "variant_id": variant_id, "quantity": quantity}],
        },
    )
    assert billed.status_code == 201, billed.get_json()
    return billed.get_json()["data"]


def test_restaurant_returns_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    denied = client.get("/api/v1/returns", headers=headers)
    assert denied.status_code == 403


def test_return_restocks_correct_variant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers)
    tee = _item(client, headers, cat_id, "Return Tee")
    medium = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "M", "color": "Black", "stock_quantity": "4"},
    ).get_json()["data"]
    large = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "L", "color": "Black", "stock_quantity": "4"},
    ).get_json()["data"]

    bill = _sell(client, headers, tee["id"], medium["id"], "2")
    bill_line = bill["items"][0]

    lookup = client.get(
        "/api/v1/returns/lookup",
        headers=headers,
        query_string={"bill_number": bill["bill_number"]},
    )
    assert lookup.status_code == 200, lookup.get_json()
    assert float(lookup.get_json()["data"]["items"][0]["quantity_returnable"]) == 2.0

    created = client.post(
        "/api/v1/returns",
        headers=headers,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Wrong size",
            "items": [{"bill_item_id": bill_line["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["kind"] == "RETURN"
    assert float(body["refund_amount"]) == 200.0

    stocks = {
        row["id"]: float(row["stock_quantity"])
        for row in client.get(f"/api/v1/items/{tee['id']}/variants", headers=headers).get_json()["data"]
    }
    assert stocks[medium["id"]] == 3.0  # 4 - 2 sold + 1 returned
    assert stocks[large["id"]] == 4.0

    over = client.post(
        "/api/v1/returns",
        headers=headers,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Too much",
            "items": [{"bill_item_id": bill_line["id"], "quantity": "2"}],
        },
    )
    assert over.status_code == 400


def test_exchange_swaps_variant_stock(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers)
    tee = _item(client, headers, cat_id, "Swap Tee")
    small = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "S", "color": "Red", "stock_quantity": "2"},
    ).get_json()["data"]
    large = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "L", "color": "Red", "stock_quantity": "5"},
    ).get_json()["data"]
    bill = _sell(client, headers, tee["id"], small["id"], "1")

    swapped = client.post(
        "/api/v1/returns",
        headers=headers,
        json={
            "bill_id": bill["id"],
            "kind": "EXCHANGE",
            "reason": "Need larger size",
            "items": [
                {
                    "bill_item_id": bill["items"][0]["id"],
                    "quantity": "1",
                    "exchange_item_id": tee["id"],
                    "exchange_variant_id": large["id"],
                }
            ],
        },
    )
    assert swapped.status_code == 201, swapped.get_json()
    stocks = {
        row["id"]: float(row["stock_quantity"])
        for row in client.get(f"/api/v1/items/{tee['id']}/variants", headers=headers).get_json()["data"]
    }
    assert stocks[small["id"]] == 2.0  # sold 1 then restocked
    assert stocks[large["id"]] == 4.0  # exchanged out


def test_billing_user_cannot_create_return(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_clothing(client, owner)
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, "Staff Tee")
    variant = client.post(
        f"/api/v1/items/{item['id']}/variants",
        headers=owner,
        json={"size": "M", "color": "White", "stock_quantity": "3"},
    ).get_json()["data"]
    bill = _sell(client, owner, item["id"], variant["id"])

    listing = client.get("/api/v1/returns", headers=billing)
    assert listing.status_code == 200, listing.get_json()

    denied = client.post(
        "/api/v1/returns",
        headers=billing,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Trying",
            "items": [{"bill_item_id": bill["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert denied.status_code == 403


def test_return_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_clothing(client, owner_a)
    _switch_clothing(client, owner_b)
    cat_id = _category(client, owner_a)
    item = _item(client, owner_a, cat_id, "Iso Tee")
    variant = client.post(
        f"/api/v1/items/{item['id']}/variants",
        headers=owner_a,
        json={"size": "M", "color": "Grey", "stock_quantity": "2"},
    ).get_json()["data"]
    bill = _sell(client, owner_a, item["id"], variant["id"])
    created = client.post(
        "/api/v1/returns",
        headers=owner_a,
        json={
            "bill_id": bill["id"],
            "kind": "RETURN",
            "reason": "Isolation",
            "items": [{"bill_item_id": bill["items"][0]["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    other = client.get(f"/api/v1/returns/{created.get_json()['data']['id']}", headers=owner_b)
    assert other.status_code in {403, 404}
    lookup = client.get(
        "/api/v1/returns/lookup",
        headers=owner_b,
        query_string={"bill_number": bill["bill_number"]},
    )
    assert lookup.status_code == 404
