"""Category and item API tests."""

from app.extensions import db
from app.models.audit_log import AuditLog
from tests.conftest import login


def test_owner_creates_category_and_item(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")

    cat_res = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": "Main Course", "description": "Meals"},
    )
    assert cat_res.status_code == 201
    category_id = cat_res.get_json()["data"]["id"]

    item_res = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": "Chicken Thali",
            "category_id": category_id,
            "price": 420,
            "gst_percentage": 5,
        },
    )
    assert item_res.status_code == 201
    item = item_res.get_json()["data"]
    assert item["price"] == 420.0
    assert item["gst_percentage"] == 5.0
    assert item["category_name"] == "Main Course"


def test_billing_user_sees_only_active_items(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Beverages"},
    ).get_json()["data"]["id"]

    active_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Masala Tea",
            "category_id": category_id,
            "price": 30,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]

    inactive_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Old Shake",
            "category_id": category_id,
            "price": 80,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]

    client.patch(
        f"/api/v1/items/{inactive_id}/status",
        headers=owner,
        json={"is_active": False},
    )

    billing_items = client.get("/api/v1/items", headers=billing).get_json()["data"]
    ids = {i["id"] for i in billing_items}
    assert active_id in ids
    assert inactive_id not in ids


def test_billing_user_cannot_create_item(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Snacks"},
    ).get_json()["data"]["id"]

    response = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "Samosa",
            "category_id": category_id,
            "price": 20,
            "gst_percentage": 5,
        },
    )
    assert response.status_code == 403


def test_price_and_gst_changes_are_audited(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Rice"},
    ).get_json()["data"]["id"]
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Jeera Rice",
            "category_id": category_id,
            "price": 220,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]

    response = client.put(
        f"/api/v1/items/{item_id}",
        headers=owner,
        json={"price": 250, "gst_percentage": 2.5},
    )
    assert response.status_code == 200

    actions = {
        row.action
        for row in db.session.query(AuditLog)
        .filter(AuditLog.entity_id == item_id, AuditLog.entity_type == "ITEM")
        .all()
    }
    assert "UPDATE_PRICE" in actions
    assert "CHANGE_GST" in actions


def test_cross_tenant_category_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    category_a = client.post(
        "/api/v1/categories",
        headers=owner_a,
        json={"name": "Tenant A Only"},
    ).get_json()["data"]

    response = client.get(f"/api/v1/categories/{category_a['id']}", headers=owner_b)
    assert response.status_code == 404

    list_b = client.get("/api/v1/categories", headers=owner_b).get_json()["data"]
    assert all(c["name"] != "Tenant A Only" for c in list_b)


def test_item_search(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Thali"},
    ).get_json()["data"]["id"]
    client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Mutton Sadhi Thali",
            "category_id": category_id,
            "price": 480,
            "gst_percentage": 5,
        },
    )
    client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Veg Thali",
            "category_id": category_id,
            "price": 280,
            "gst_percentage": 5,
        },
    )

    result = client.get("/api/v1/items?q=mutton", headers=owner).get_json()["data"]
    assert len(result) == 1
    assert result[0]["name"] == "Mutton Sadhi Thali"
