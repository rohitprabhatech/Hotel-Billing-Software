"""Billing user item management + owner item activity visibility."""

from app.extensions import db
from app.models.audit_log import AuditLog
from tests.conftest import login


def _category(client, headers, name="Non-Veg"):
    return client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": name},
    ).get_json()["data"]["id"]


def test_billing_user_creates_item_with_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _category(client, owner, "Non-Veg Menu")

    response = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "Chicken Biryani",
            "category_id": category_id,
            "price": 250,
            "gst_percentage": 2.5,
        },
    )
    assert response.status_code == 201, response.get_json()
    item = response.get_json()["data"]
    assert item["created_by_name"] == "Billing A"
    assert item["price"] == 250.0

    actions = {
        row.action
        for row in db.session.query(AuditLog).filter(
            AuditLog.entity_id == item["id"], AuditLog.entity_type == "ITEM"
        )
    }
    assert "ITEM_CREATED" in actions

    owner_logs = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"entity_type": "ITEM", "action": "ITEM_CREATED"},
    )
    assert owner_logs.status_code == 200
    assert any(row["entity_id"] == item["id"] for row in owner_logs.get_json()["data"])


def test_billing_user_creates_category_with_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    response = client.post(
        "/api/v1/categories",
        headers=billing,
        json={"name": "Chinese Food", "description": "Chinese food items"},
    )
    assert response.status_code == 201, response.get_json()
    category = response.get_json()["data"]
    assert category["name"] == "Chinese Food"

    actions = {
        row.action
        for row in db.session.query(AuditLog).filter(
            AuditLog.entity_id == category["id"], AuditLog.entity_type == "CATEGORY"
        )
    }
    assert "CREATE_CATEGORY" in actions

    owner_logs = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"entity_type": "CATEGORY", "action": "CREATE_CATEGORY"},
    )
    assert owner_logs.status_code == 200
    assert any(row["entity_id"] == category["id"] for row in owner_logs.get_json()["data"])

    updated = client.put(
        f"/api/v1/categories/{category['id']}",
        headers=billing,
        json={"name": "Chinese Special", "description": "Updated"},
    )
    assert updated.status_code == 200, updated.get_json()
    assert updated.get_json()["data"]["name"] == "Chinese Special"

    duplicate = client.post(
        "/api/v1/categories",
        headers=billing,
        json={"name": "Chinese Special"},
    )
    assert duplicate.status_code == 409, duplicate.get_json()

    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    foreign = client.get(f"/api/v1/categories/{category['id']}", headers=owner_b)
    assert foreign.status_code == 404


def test_billing_cannot_deactivate_category_with_items(client):
    billing = login(client, "billing@hotela.com", "Billing@12345")
    cat = client.post(
        "/api/v1/categories",
        headers=billing,
        json={"name": "Has Items Cat"},
    ).get_json()["data"]
    item = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "Noodles",
            "category_id": cat["id"],
            "price": 150,
            "gst_percentage": 5,
        },
    )
    assert item.status_code == 201, item.get_json()

    blocked = client.patch(
        f"/api/v1/categories/{cat['id']}/status",
        headers=billing,
        json={"is_active": False},
    )
    assert blocked.status_code == 400, blocked.get_json()
    assert "item" in blocked.get_json()["error"]["message"].lower()


def test_billing_user_updates_and_deactivates_item(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _category(client, owner, "Rice Items")
    item_id = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "Jeera Special",
            "category_id": category_id,
            "price": 220,
            "gst_percentage": 2.5,
        },
    ).get_json()["data"]["id"]

    updated = client.put(
        f"/api/v1/items/{item_id}",
        headers=billing,
        json={"price": 280},
    )
    assert updated.status_code == 200
    assert updated.get_json()["data"]["price"] == 280.0

    deactivated = client.patch(
        f"/api/v1/items/{item_id}/status",
        headers=billing,
        json={"is_active": False, "reason": "Item temporarily unavailable"},
    )
    assert deactivated.status_code == 200
    assert deactivated.get_json()["data"]["is_active"] is False

    actions = {
        row.action: row
        for row in db.session.query(AuditLog).filter(
            AuditLog.entity_id == item_id, AuditLog.entity_type == "ITEM"
        )
    }
    assert "ITEM_UPDATED" in actions
    assert "ITEM_DEACTIVATED" in actions
    assert actions["ITEM_DEACTIVATED"].new_data.get("reason") == "Item temporarily unavailable"

    # Inactive items excluded from active billing catalog
    catalog = client.get(
        "/api/v1/items",
        headers=billing,
        query_string={"is_active": "true"},
    ).get_json()["data"]
    assert item_id not in {i["id"] for i in catalog}

    # Management list still shows inactive item
    all_items = client.get("/api/v1/items", headers=billing).get_json()["data"]
    assert item_id in {i["id"] for i in all_items}


def test_hard_delete_item_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _category(client, owner, "Drinks")
    item_id = client.post(
        "/api/v1/items",
        headers=billing,
        json={"name": "Pepsi Can", "category_id": category_id, "price": 50, "gst_percentage": 2.5},
    ).get_json()["data"]["id"]

    response = client.delete(f"/api/v1/items/{item_id}", headers=billing)
    assert response.status_code in {403, 405}


def test_billing_cannot_delete_or_access_foreign_audit(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    category_id = _category(client, owner_a, "Audit Cat")
    item_id = client.post(
        "/api/v1/items",
        headers=billing,
        json={"name": "Audit Item", "category_id": category_id, "price": 100, "gst_percentage": 2.5},
    ).get_json()["data"]["id"]

    log = (
        db.session.query(AuditLog)
        .filter(AuditLog.entity_id == item_id, AuditLog.action == "ITEM_CREATED")
        .first()
    )
    assert log is not None

    assert client.delete(f"/api/v1/audit-logs/{log.id}", headers=billing).status_code == 403
    assert client.get("/api/v1/audit-logs", headers=billing).status_code == 403
    assert client.get(f"/api/v1/audit-logs/{log.id}", headers=owner_b).status_code == 404


def test_owner_reactivates_item_audited(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _category(client, owner, "Reactivate Cat")
    item_id = client.post(
        "/api/v1/items",
        headers=billing,
        json={"name": "Temp Item", "category_id": category_id, "price": 90, "gst_percentage": 2.5},
    ).get_json()["data"]["id"]
    client.patch(
        f"/api/v1/items/{item_id}/status",
        headers=billing,
        json={"is_active": False},
    )
    response = client.patch(
        f"/api/v1/items/{item_id}/status",
        headers=owner,
        json={"is_active": True},
    )
    assert response.status_code == 200
    actions = {
        row.action
        for row in db.session.query(AuditLog).filter(AuditLog.entity_id == item_id)
    }
    assert "ITEM_REACTIVATED" in actions


def test_price_change_keeps_historical_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _category(client, owner, "History Cat")
    item_id = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "History Biryani",
            "category_id": category_id,
            "price": 250,
            "gst_percentage": 2.5,
        },
    ).get_json()["data"]["id"]

    bill_a = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item_id, "quantity": 1}], "discount": 0},
    )
    assert bill_a.status_code == 201
    bill_a_id = bill_a.get_json()["data"]["id"]
    assert bill_a.get_json()["data"]["items"][0]["unit_price"] == 250.0

    client.put(
        f"/api/v1/items/{item_id}",
        headers=billing,
        json={"price": 300},
    )
    bill_b = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item_id, "quantity": 1}], "discount": 0},
    )
    assert bill_b.status_code == 201
    assert bill_b.get_json()["data"]["items"][0]["unit_price"] == 300.0

    historical = client.get(f"/api/v1/bills/{bill_a_id}", headers=owner).get_json()["data"]
    assert historical["items"][0]["unit_price"] == 250.0


def test_owner_filters_item_activity_by_user(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _category(client, owner, "Filter Cat")
    client.post(
        "/api/v1/items",
        headers=billing,
        json={"name": "Filter Item", "category_id": category_id, "price": 40, "gst_percentage": 0},
    )
    users = client.get("/api/v1/users", headers=owner).get_json()["data"]
    billing_user = next(u for u in users if u["role"] == "BILLING_USER")
    logs = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={
            "entity_type": "ITEM",
            "user_id": billing_user["id"],
            "action": "ITEM_CREATED",
        },
    ).get_json()["data"]
    assert logs
    assert all(row["user_id"] == billing_user["id"] for row in logs)


def test_item_sku_cost_stock_and_search(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = _category(client, owner, "Retail Cat")

    created = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "Cotton Shirt",
            "sku": "SKU-SHIRT-01",
            "category_id": category_id,
            "price": 799,
            "cost_price": 420,
            "gst_percentage": 5,
            "stock_quantity": 12,
            "description": "Men formal shirt",
        },
    )
    assert created.status_code == 201, created.get_json()
    item = created.get_json()["data"]
    assert item["sku"] == "SKU-SHIRT-01"
    assert item["cost_price"] == 420.0
    assert item["stock_quantity"] == 12.0

    duplicate = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "Another Shirt",
            "sku": "sku-shirt-01",
            "category_id": category_id,
            "price": 500,
            "gst_percentage": 5,
        },
    )
    assert duplicate.status_code == 409

    found = client.get(
        "/api/v1/items",
        headers=owner,
        query_string={"q": "SKU-SHIRT"},
    ).get_json()["data"]
    assert any(row["id"] == item["id"] for row in found)

    updated = client.put(
        f"/api/v1/items/{item['id']}",
        headers=billing,
        json={"stock_quantity": 9, "cost_price": 410},
    )
    assert updated.status_code == 200
    assert updated.get_json()["data"]["stock_quantity"] == 9.0
    assert updated.get_json()["data"]["cost_price"] == 410.0

    cleared = client.put(
        f"/api/v1/items/{item['id']}",
        headers=owner,
        json={"stock_quantity": None, "sku": None},
    )
    assert cleared.status_code == 200
    assert cleared.get_json()["data"]["stock_quantity"] is None
    assert cleared.get_json()["data"]["sku"] is None
