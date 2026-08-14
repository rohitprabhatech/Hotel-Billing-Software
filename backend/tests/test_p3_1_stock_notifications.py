"""P3-1: stock enforcement, cancel restore, notifications."""

from tests.conftest import login


def _category_and_item(client, headers, *, name, stock, minimum=None, price=100):
    category_id = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": f"Cat-{name}"},
    ).get_json()["data"]["id"]
    payload = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "gst_percentage": 0,
        "stock_quantity": stock,
    }
    if minimum is not None:
        payload["minimum_stock_level"] = minimum
    item = client.post("/api/v1/items", headers=headers, json=payload).get_json()["data"]
    return item


def test_insufficient_stock_rejects_and_leaves_stock_unchanged(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(client, owner, name="Rice Stock", stock=10, minimum=5)

    ok = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 5}], "payment_method": "cash"},
    )
    assert ok.status_code == 201, ok.get_json()

    after = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert after["stock_quantity"] == 5.0

    blocked = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 6}], "payment_method": "cash"},
    )
    assert blocked.status_code == 400
    body = blocked.get_json()
    assert body["success"] is False
    assert body["error"]["code"] == "INSUFFICIENT_STOCK"
    assert "Available: 5" in body["error"]["message"]
    assert "requested: 6" in body["error"]["message"]

    still = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert still["stock_quantity"] == 5.0


def test_multi_item_bill_rejects_without_partial_deduction(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item_a = _category_and_item(client, owner, name="Stock A", stock=10)
    item_b = _category_and_item(client, owner, name="Stock B", stock=3)

    response = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [
                {"item_id": item_a["id"], "quantity": 5},
                {"item_id": item_b["id"], "quantity": 5},
            ],
        },
    )
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"

    a = client.get(f"/api/v1/items/{item_a['id']}", headers=owner).get_json()["data"]
    b = client.get(f"/api/v1/items/{item_b['id']}", headers=owner).get_json()["data"]
    assert a["stock_quantity"] == 10.0
    assert b["stock_quantity"] == 3.0


def test_cancel_restores_stock(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(client, owner, name="Restore Item", stock=10)

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 4}], "payment_method": "online"},
    ).get_json()["data"]
    assert (
        client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"][
            "stock_quantity"
        ]
        == 6.0
    )

    cancelled = client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=owner,
        json={"reason": "Customer returned"},
    )
    assert cancelled.status_code == 200
    assert (
        client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"][
            "stock_quantity"
        ]
        == 10.0
    )


def test_null_stock_untracked_allows_any_qty(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(client, owner, name="Untracked", stock=None)
    assert item["stock_quantity"] is None
    response = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 50}], "payment_method": "cash"},
    )
    assert response.status_code == 201


def test_low_stock_notification_and_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    billing_a = login(client, "billing@hotela.com", "Billing@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    item = _category_and_item(
        client, owner_a, name="Notify Rice", stock=10, minimum=5, price=50
    )
    client.post(
        "/api/v1/bills",
        headers=billing_a,
        json={"items": [{"item_id": item["id"], "quantity": 6}], "payment_method": "cash"},
    )

    notes = client.get("/api/v1/notifications", headers=owner_a).get_json()["data"]
    assert any(n["type"] == "LOW_STOCK" and "Notify Rice" in n["message"] for n in notes)

    billing_notes = client.get("/api/v1/notifications", headers=billing_a).get_json()["data"]
    assert any(n["type"] == "LOW_STOCK" for n in billing_notes)

    notes_b = client.get("/api/v1/notifications", headers=owner_b).get_json()["data"]
    assert not any("Notify Rice" in (n.get("message") or "") for n in notes_b)

    # Duplicate control: another bill that stays low should not spam new unread LOW_STOCK
    # Sell 1 more (stock 3) — still low, already have unread LOW_STOCK
    client.post(
        "/api/v1/bills",
        headers=billing_a,
        json={"items": [{"item_id": item["id"], "quantity": 1}], "payment_method": "cash"},
    )
    low_count = sum(
        1
        for n in client.get("/api/v1/notifications", headers=owner_a).get_json()["data"]
        if n["type"] == "LOW_STOCK" and n["entity_id"] == item["id"]
    )
    assert low_count == 1


def test_out_of_stock_then_reject(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(client, owner, name="Empty Me", stock=2, minimum=1)

    assert (
        client.post(
            "/api/v1/bills",
            headers=billing,
            json={"items": [{"item_id": item["id"], "quantity": 2}], "payment_method": "cash"},
        ).status_code
        == 201
    )
    notes = client.get("/api/v1/notifications", headers=owner).get_json()["data"]
    assert any(n["type"] == "OUT_OF_STOCK" and "Empty Me" in n["message"] for n in notes)

    blocked = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 1}], "payment_method": "cash"},
    )
    assert blocked.status_code == 400
    assert blocked.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"
    assert "out of stock" in blocked.get_json()["error"]["message"].lower()


def test_mark_notification_read(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(client, owner, name="Read Note Item", stock=3, minimum=2)
    client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 2}], "payment_method": "cash"},
    )
    rows = client.get("/api/v1/notifications", headers=owner).get_json()["data"]
    assert rows
    nid = rows[0]["id"]
    marked = client.patch(f"/api/v1/notifications/{nid}/read", headers=owner)
    assert marked.status_code == 200
    assert marked.get_json()["data"]["is_read"] is True
    count = client.get("/api/v1/notifications/unread-count", headers=owner).get_json()["data"]
    assert "unread_count" in count
