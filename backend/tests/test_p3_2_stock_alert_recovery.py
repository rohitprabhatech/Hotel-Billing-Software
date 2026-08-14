"""P3-2: restock clears open stock alerts; cancel restore resolves notifications."""

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
    return client.post("/api/v1/items", headers=headers, json=payload).get_json()["data"]


def test_restock_marks_low_stock_alert_read(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(
        client, owner, name="Restock Clear", stock=10, minimum=5, price=40
    )

    # Cross into low stock
    client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 6}], "payment_method": "cash"},
    )
    notes = client.get(
        "/api/v1/notifications", headers=owner, query_string={"unread_only": True}
    ).get_json()["data"]
    assert any(
        n["type"] == "LOW_STOCK" and n["entity_id"] == item["id"] and not n["is_read"]
        for n in notes
    )

    # Owner restocks above minimum
    updated = client.put(
        f"/api/v1/items/{item['id']}",
        headers=owner,
        json={"stock_quantity": 20},
    )
    assert updated.status_code == 200, updated.get_json()

    unread = client.get(
        "/api/v1/notifications", headers=owner, query_string={"unread_only": True}
    ).get_json()["data"]
    assert not any(
        n["type"] == "LOW_STOCK" and n["entity_id"] == item["id"] for n in unread
    )

    all_notes = client.get("/api/v1/notifications", headers=owner).get_json()["data"]
    matching = [
        n for n in all_notes if n["type"] == "LOW_STOCK" and n["entity_id"] == item["id"]
    ]
    assert matching
    assert all(n["is_read"] for n in matching)


def test_cancel_restores_and_clears_out_of_stock_alert(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(
        client, owner, name="Cancel Clear OOS", stock=3, minimum=1, price=25
    )

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 3}], "payment_method": "cash"},
    ).get_json()["data"]

    unread = client.get(
        "/api/v1/notifications", headers=owner, query_string={"unread_only": True}
    ).get_json()["data"]
    assert any(
        n["type"] == "OUT_OF_STOCK" and n["entity_id"] == item["id"] for n in unread
    )

    cancelled = client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=owner,
        json={"reason": "Restock via cancel"},
    )
    assert cancelled.status_code == 200

    after = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert after["stock_quantity"] == 3.0

    unread_after = client.get(
        "/api/v1/notifications", headers=owner, query_string={"unread_only": True}
    ).get_json()["data"]
    assert not any(
        n["type"] == "OUT_OF_STOCK" and n["entity_id"] == item["id"] for n in unread_after
    )
