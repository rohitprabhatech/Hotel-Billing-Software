"""Sprint BIZ-15 — restaurant order settlement and split billing."""

from decimal import Decimal

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, stock="20", price="200"):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "gst_percentage": "5",
        "stock_quantity": stock,
    }
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _table(client, headers, code):
    response = client.post("/api/v1/tables", headers=headers, json={"code": code, "capacity": 4})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _dine_in_order(client, headers, table_id, items):
    response = client.post(
        "/api/v1/orders",
        headers=headers,
        json={"channel": "dine_in", "dining_table_id": table_id, "items": items},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_settle_open_order_creates_bill(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Settle Cat")
    item = _item(client, headers, cat_id, "Settle Item")
    table = _table(client, headers, "S-T1")
    order = _dine_in_order(
        client,
        headers,
        table["id"],
        [{"item_id": item["id"], "quantity": "2"}],
    )

    settled = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash", "service_charge": "20", "discount": "10"},
    )
    assert settled.status_code == 201, settled.get_json()
    body = settled.get_json()["data"]
    assert body["order"]["status"] == "BILLED"
    assert body["order"]["bill_id"] is not None
    assert len(body["bills"]) == 1
    bill = body["bills"][0]
    assert bill["order_id"] == order["id"]
    assert bill["service_charge"] == 20.0
    assert bill["payment_method"] == "cash"

    table_state = client.get(f"/api/v1/tables/{table['id']}", headers=headers).get_json()["data"]
    assert table_state["status"] == "available"

    item_state = client.get(f"/api/v1/items/{item['id']}", headers=headers).get_json()["data"]
    assert item_state["stock_quantity"] == 18.0


def test_cannot_settle_cancelled_order(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Settle Cancel Cat")
    item = _item(client, headers, cat_id, "Settle Cancel Item")
    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]
    client.post(f"/api/v1/orders/{order['id']}/cancel", headers=headers, json={"reason": "x"})

    denied = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert denied.status_code == 400, denied.get_json()


def test_split_bill_totals_match_single_settle(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Split Cat")
    item_a = _item(client, headers, cat_id, "Split A", price="300")
    item_b = _item(client, headers, cat_id, "Split B", price="200")

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [
                {"item_id": item_a["id"], "quantity": "1"},
                {"item_id": item_b["id"], "quantity": "1"},
            ],
        },
    ).get_json()["data"]

    single = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash", "discount": "50", "service_charge": "30"},
    )
    assert single.status_code == 201, single.get_json()
    single_total = single.get_json()["data"]["bills"][0]["grand_total"]

    order2 = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [
                {"item_id": item_a["id"], "quantity": "1"},
                {"item_id": item_b["id"], "quantity": "1"},
            ],
        },
    ).get_json()["data"]
    line2_a, line2_b = order2["items"][0]["id"], order2["items"][1]["id"]

    split = client.post(
        "/api/v1/bills/split",
        headers=headers,
        json={
            "order_id": order2["id"],
            "discount": 50,
            "service_charge": 30,
            "splits": [
                {"order_item_ids": [line2_a], "payment_method": "cash"},
                {"order_item_ids": [line2_b], "payment_method": "online"},
            ],
        },
    )
    assert split.status_code == 201, split.get_json()
    split_body = split.get_json()["data"]
    assert len(split_body["bills"]) == 2
    split_total = sum(b["grand_total"] for b in split_body["bills"])
    assert Decimal(str(split_total)) == Decimal(str(single_total))
    assert split_body["split_group_id"] is not None


def test_settle_blocks_insufficient_stock(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Stock Block Cat")
    item = _item(client, headers, cat_id, "Stock Block Item", stock="1")
    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "3"}],
        },
    ).get_json()["data"]

    denied = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert denied.status_code == 400, denied.get_json()
    assert denied.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"

    refreshed = client.get(f"/api/v1/orders/{order['id']}", headers=headers).get_json()["data"]
    assert refreshed["status"] == "OPEN"


def test_settle_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, owner_a, "Settle Iso Cat")
    item = _item(client, owner_a, cat_id, "Settle Iso Item")
    order = client.post(
        "/api/v1/orders",
        headers=owner_a,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    denied = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=owner_b,
        json={"payment_method": "cash"},
    )
    assert denied.status_code == 404, denied.get_json()
