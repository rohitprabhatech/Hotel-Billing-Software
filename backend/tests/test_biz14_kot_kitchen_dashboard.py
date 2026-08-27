"""Sprint BIZ-14 — KOT and kitchen dashboard."""

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


def _open_order(client, headers, item_id):
    response = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "customer_name": "KOT Guest",
            "items": [{"item_id": item_id, "quantity": "2"}],
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_fire_kot_for_open_order(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "KOT Cat")
    item = _item(client, headers, cat_id, "KOT Item")
    order = _open_order(client, headers, item["id"])

    fired = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers)
    assert fired.status_code == 201, fired.get_json()
    kot = fired.get_json()["data"]
    assert kot["order_id"] == order["id"]
    assert kot["status"] == "queued"
    assert kot["kot_number"].startswith("KOT-")
    assert len(kot["items"]) == 1
    assert kot["items"][0]["item_name"] == "KOT Item"
    assert kot["print_count"] == 1

    queue = client.get("/api/v1/kots/kitchen/queue", headers=headers)
    assert queue.status_code == 200, queue.get_json()
    queue_ids = [row["id"] for row in queue.get_json()["data"]]
    assert kot["id"] in queue_ids


def test_kot_reprint_is_idempotent(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Reprint Cat")
    item = _item(client, headers, cat_id, "Reprint Item")
    order = _open_order(client, headers, item["id"])

    first = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers).get_json()["data"]
    second = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers)
    assert second.status_code == 201, second.get_json()
    body = second.get_json()["data"]
    assert body["id"] == first["id"]
    assert body["print_count"] == 2


def test_kot_incremental_for_new_items(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Inc KOT Cat")
    item_a = _item(client, headers, cat_id, "Inc Item A")
    item_b = _item(client, headers, cat_id, "Inc Item B")
    order = _open_order(client, headers, item_a["id"])

    first = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers)
    assert first.status_code == 201, first.get_json()
    first_kot = first.get_json()["data"]
    assert len(first_kot["items"]) == 1

    added = client.post(
        f"/api/v1/orders/{order['id']}/items",
        headers=headers,
        json={"item_id": item_b["id"], "quantity": "1"},
    )
    assert added.status_code in (200, 201), added.get_json()

    second = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers)
    assert second.status_code == 201, second.get_json()
    second_kot = second.get_json()["data"]
    assert second_kot["id"] != first_kot["id"]
    assert len(second_kot["items"]) == 1
    assert second_kot["items"][0]["item_name"] == "Inc Item B"


def test_kot_not_allowed_for_cancelled_order(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Cancel KOT Cat")
    item = _item(client, headers, cat_id, "Cancel KOT Item")
    order = _open_order(client, headers, item["id"])

    cancelled = client.post(
        f"/api/v1/orders/{order['id']}/cancel",
        headers=headers,
        json={"reason": "No show"},
    )
    assert cancelled.status_code == 200, cancelled.get_json()

    denied = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers)
    assert denied.status_code == 400, denied.get_json()


def test_kot_status_flow(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Status Cat")
    item = _item(client, headers, cat_id, "Status Item")
    order = _open_order(client, headers, item["id"])
    kot = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers).get_json()["data"]

    preparing = client.patch(
        f"/api/v1/kots/{kot['id']}/status",
        headers=headers,
        json={"status": "preparing"},
    )
    assert preparing.status_code == 200, preparing.get_json()
    assert preparing.get_json()["data"]["status"] == "preparing"

    ready = client.patch(
        f"/api/v1/kots/{kot['id']}/status",
        headers=headers,
        json={"status": "ready"},
    )
    assert ready.status_code == 200, ready.get_json()
    assert ready.get_json()["data"]["status"] == "ready"


def test_kot_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, owner_a, "KOT Iso Cat")
    item = _item(client, owner_a, cat_id, "KOT Iso Item")
    order = _open_order(client, owner_a, item["id"])
    kot = client.post(f"/api/v1/orders/{order['id']}/kot", headers=owner_a).get_json()["data"]

    denied = client.get(f"/api/v1/kots/{kot['id']}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_kitchen_api_forbidden_without_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    response = client.get("/api/v1/kots/kitchen/queue", headers=headers)
    assert response.status_code == 403, response.get_json()


def test_kot_create_audit_log(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Audit KOT Cat")
    item = _item(client, headers, cat_id, "Audit KOT Item")
    order = _open_order(client, headers, item["id"])
    kot = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers).get_json()["data"]

    logs = client.get(
        "/api/v1/audit-logs",
        headers=headers,
        query_string={"action": "CREATE_KOT", "per_page": 10},
    ).get_json()["data"]
    assert any(row["entity_id"] == kot["id"] for row in logs)


def test_owner_can_update_and_delete_kot(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    cat_id = _category(client, owner, "Edit KOT Cat")
    item = _item(client, owner, cat_id, "Edit KOT Item")
    order = _open_order(client, owner, item["id"])
    kot = client.post(f"/api/v1/orders/{order['id']}/kot", headers=owner).get_json()["data"]
    line_id = kot["items"][0]["id"]

    denied = client.patch(
        f"/api/v1/kots/{kot['id']}",
        headers=billing,
        json={"notes": "Less spicy", "items": [{"id": line_id, "quantity": "3"}]},
    )
    assert denied.status_code == 403, denied.get_json()

    updated = client.patch(
        f"/api/v1/kots/{kot['id']}",
        headers=owner,
        json={
            "notes": "Less spicy",
            "status": "preparing",
            "items": [{"id": line_id, "quantity": "3"}],
        },
    )
    assert updated.status_code == 200, updated.get_json()
    body = updated.get_json()["data"]
    assert body["id"] == kot["id"]
    assert body["notes"] == "Less spicy"
    assert body["status"] == "preparing"
    assert body["items"][0]["quantity"] == 3.0

    logs = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "UPDATE_KOT", "per_page": 10},
    ).get_json()["data"]
    assert any(row["entity_id"] == kot["id"] for row in logs)

    deleted = client.delete(f"/api/v1/kots/{kot['id']}", headers=owner)
    assert deleted.status_code == 200, deleted.get_json()
    assert deleted.get_json()["data"]["status"] == "cancelled"

    queue = client.get("/api/v1/kots/kitchen/queue", headers=owner).get_json()["data"]
    assert kot["id"] not in [row["id"] for row in queue]

    delete_logs = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "DELETE_KOT", "per_page": 10},
    ).get_json()["data"]
    assert any(row["entity_id"] == kot["id"] for row in delete_logs)

    billing_delete = client.delete(f"/api/v1/kots/{kot['id']}", headers=billing)
    assert billing_delete.status_code == 403, billing_delete.get_json()
