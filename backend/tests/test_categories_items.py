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

    billing_items = client.get(
        "/api/v1/items",
        headers=billing,
        query_string={"is_active": "true"},
    ).get_json()["data"]
    ids = {i["id"] for i in billing_items}
    assert active_id in ids
    assert inactive_id not in ids


def test_billing_user_can_create_item(client):
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
    assert response.status_code == 201
    assert response.get_json()["data"]["name"] == "Samosa"


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
    assert "ITEM_UPDATED" in actions
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

    # Business B cannot use Business A category as parent
    bad_parent = client.post(
        "/api/v1/categories",
        headers=owner_b,
        json={"name": "Should Fail", "parent_id": category_a["id"]},
    )
    assert bad_parent.status_code == 400


def test_parent_category_hierarchy_and_validation(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")

    food = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Food Hierarchy", "description": "Root food", "parent_id": None},
    ).get_json()["data"]
    assert food["parent_id"] is None
    assert food["parent_category_name"] is None
    assert food["hierarchy_path"] == "Food Hierarchy"

    veg = client.post(
        "/api/v1/categories",
        headers=owner,
        json={
            "name": "Veg Hierarchy",
            "description": "Vegetarian",
            "parent_category_id": food["id"],
        },
    ).get_json()["data"]
    assert veg["parent_id"] == food["id"]
    assert veg["parent_category_name"] == "Food Hierarchy"
    assert veg["hierarchy_path"] == "Food Hierarchy › Veg Hierarchy"

    non_veg = client.post(
        "/api/v1/categories",
        headers=owner,
        json={
            "name": "Non-Veg Hierarchy",
            "parent_id": food["id"],
        },
    ).get_json()["data"]
    assert non_veg["parent_category_id"] == food["id"]

    # Self-parent not allowed
    self_parent = client.put(
        f"/api/v1/categories/{food['id']}",
        headers=owner,
        json={"parent_id": food["id"]},
    )
    assert self_parent.status_code == 400
    assert "own parent" in self_parent.get_json()["error"]["message"].lower()

    # Circular hierarchy not allowed (Food -> parent = Veg)
    circular = client.put(
        f"/api/v1/categories/{food['id']}",
        headers=owner,
        json={"parent_id": veg["id"]},
    )
    assert circular.status_code == 400
    assert "circular" in circular.get_json()["error"]["message"].lower()

    # Cannot deactivate parent with children
    deactivate = client.patch(
        f"/api/v1/categories/{food['id']}/status",
        headers=owner,
        json={"is_active": False},
    )
    assert deactivate.status_code == 400
    assert "child" in deactivate.get_json()["error"]["message"].lower()

    listed = client.get("/api/v1/categories", headers=owner).get_json()["data"]
    by_id = {row["id"]: row for row in listed}
    assert by_id[veg["id"]]["parent_category_name"] == "Food Hierarchy"
    assert by_id[veg["id"]]["hierarchy_path"] == "Food Hierarchy › Veg Hierarchy"


def test_clothing_category_hierarchy_sample(client):
    """Retail-style nested categories (Clothing › Men › Shirts)."""
    owner = login(client, "owner@hotela.com", "Owner@12345")

    clothing = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Clothing Sample", "parent_id": None},
    ).get_json()["data"]
    men = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Men Sample", "parent_id": clothing["id"]},
    ).get_json()["data"]
    shirts = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Shirts Sample", "parent_id": men["id"]},
    ).get_json()["data"]
    women = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Women Sample", "parent_id": clothing["id"]},
    ).get_json()["data"]
    dresses = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Dresses Sample", "parent_id": women["id"]},
    ).get_json()["data"]

    assert shirts["hierarchy_path"] == "Clothing Sample › Men Sample › Shirts Sample"
    assert dresses["hierarchy_path"] == "Clothing Sample › Women Sample › Dresses Sample"

    # Deeper circular check: Clothing cannot parent under Shirts
    circular = client.put(
        f"/api/v1/categories/{clothing['id']}",
        headers=owner,
        json={"parent_id": shirts["id"]},
    )
    assert circular.status_code == 400


def test_inactive_parent_rejected(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    root = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Inactive Parent Root"},
    ).get_json()["data"]
    assert (
        client.patch(
            f"/api/v1/categories/{root['id']}/status",
            headers=owner,
            json={"is_active": False},
        ).status_code
        == 200
    )
    child = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Child Of Inactive", "parent_id": root["id"]},
    )
    assert child.status_code == 400
    assert "active" in child.get_json()["error"]["message"].lower()


def test_duplicate_root_category_name_rejected(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    first = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Food Root Unique", "parent_id": None},
    )
    assert first.status_code == 201
    second = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Food Root Unique", "parent_id": None},
    )
    assert second.status_code == 409


def test_cannot_move_item_to_inactive_category(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    active_cat = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Active Cat For Move"},
    ).get_json()["data"]
    inactive_cat = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Inactive Cat For Move"},
    ).get_json()["data"]
    assert (
        client.patch(
            f"/api/v1/categories/{inactive_cat['id']}/status",
            headers=owner,
            json={"is_active": False},
        ).status_code
        == 200
    )
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Move Target Item",
            "category_id": active_cat["id"],
            "price": 10,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]
    moved = client.put(
        f"/api/v1/items/{item_id}",
        headers=owner,
        json={"category_id": inactive_cat["id"]},
    )
    assert moved.status_code == 400
    assert "inactive" in moved.get_json()["error"]["message"].lower()


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
