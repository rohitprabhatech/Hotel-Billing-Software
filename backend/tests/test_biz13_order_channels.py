"""Sprint BIZ-13 — order channels (dine-in / takeaway / delivery)."""

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "120",
        "gst_percentage": "5",
        "stock_quantity": "50",
    }
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _table(client, headers, code):
    response = client.post("/api/v1/tables", headers=headers, json={"code": code, "capacity": 4})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_dine_in_order_requires_table(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Order Cat")
    item = _item(client, headers, cat_id, "Order Item")
    table = _table(client, headers, "O-T1")

    missing_table = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "dine_in",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert missing_table.status_code == 400, missing_table.get_json()

    created = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "dine_in",
            "dining_table_id": table["id"],
            "items": [{"item_id": item["id"], "quantity": "2"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["channel"] == "dine_in"
    assert body["dining_table_id"] == table["id"]
    assert body["status"] == "OPEN"
    assert len(body["items"]) == 1

    table_state = client.get(f"/api/v1/tables/{table['id']}", headers=headers).get_json()["data"]
    assert table_state["status"] == "occupied"


def test_takeaway_order_without_table(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Takeaway Cat")
    item = _item(client, headers, cat_id, "Takeaway Item")

    created = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "customer_name": "Walk-in Guest",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["channel"] == "takeaway"
    assert body["dining_table_id"] is None


def test_delivery_requires_address(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Delivery Cat")
    item = _item(client, headers, cat_id, "Delivery Item")

    missing = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "delivery",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert missing.status_code == 400, missing.get_json()

    created = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "delivery",
            "delivery_address": "221B Baker Street",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()


def test_add_and_remove_order_lines(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Line Cat")
    item_a = _item(client, headers, cat_id, "Line Item A")
    item_b = _item(client, headers, cat_id, "Line Item B")

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item_a["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    added = client.post(
        f"/api/v1/orders/{order['id']}/items",
        headers=headers,
        json={"item_id": item_b["id"], "quantity": "2"},
    )
    assert added.status_code == 201, added.get_json()
    assert len(added.get_json()["data"]["items"]) == 2

    line_id = added.get_json()["data"]["items"][0]["id"]
    removed = client.delete(f"/api/v1/orders/{order['id']}/items/{line_id}", headers=headers)
    assert removed.status_code == 200, removed.get_json()
    assert len(removed.get_json()["data"]["items"]) == 1


def test_cancel_order_releases_table(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Cancel Cat")
    item = _item(client, headers, cat_id, "Cancel Item")
    table = _table(client, headers, "O-T2")

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "dine_in",
            "dining_table_id": table["id"],
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    cancelled = client.post(
        f"/api/v1/orders/{order['id']}/cancel",
        headers=headers,
        json={"reason": "Guest left"},
    )
    assert cancelled.status_code == 200, cancelled.get_json()
    assert cancelled.get_json()["data"]["status"] == "CANCELLED"

    table_state = client.get(f"/api/v1/tables/{table['id']}", headers=headers).get_json()["data"]
    assert table_state["status"] == "available"


def test_order_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, owner_a, "Iso Order Cat")
    item = _item(client, owner_a, cat_id, "Iso Item")

    order = client.post(
        "/api/v1/orders",
        headers=owner_a,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    denied = client.get(f"/api/v1/orders/{order['id']}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_orders_api_forbidden_without_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    response = client.get("/api/v1/orders", headers=headers)
    assert response.status_code == 403, response.get_json()


def test_billing_user_can_create_order(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    cat_id = _category(client, owner, "Billing Order Cat")
    item = _item(client, owner, cat_id, "Billing Order Item")

    created = client.post(
        "/api/v1/orders",
        headers=billing,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
