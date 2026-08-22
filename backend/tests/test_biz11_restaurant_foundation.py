"""Sprint BIZ-11 — restaurant foundation and menu extensions."""

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **extra):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "150",
        "gst_percentage": "5",
        "stock_quantity": "10",
        "uom": "pcs",
        **extra,
    }
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_restaurant_tenant_has_menu_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert response.status_code == 200, response.get_json()
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "restaurant_menu" in enabled


def test_cafe_tenant_has_menu_module(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert response.status_code == 200, response.get_json()
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "restaurant_menu" in enabled


def test_clothing_tenant_lacks_menu_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "restaurant_menu" not in enabled


def test_menu_api_allowed_for_restaurant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/menu", headers=headers)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_menu_api_forbidden_for_clothing_tenant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    response = client.get("/api/v1/menu", headers=headers)
    assert response.status_code == 403, response.get_json()
    assert response.get_json()["error"]["code"] == "FORBIDDEN"


def test_create_item_with_menu_attributes(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Main Course")
    item = _item(
        client,
        headers,
        cat_id,
        "Paneer Tikka",
        is_menu=True,
        is_veg=True,
    )
    assert item["is_menu"] is True
    assert item["is_veg"] is True


def test_menu_listing_groups_active_menu_items(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    starters = _category(client, headers, "Starters")
    beverages = _category(client, headers, "Beverages")
    _item(client, headers, starters, "Soup", is_menu=True, is_veg=True)
    _item(client, headers, beverages, "Cola", is_menu=True, is_veg=True)
    _item(client, headers, starters, "Raw Onions", is_menu=False)

    response = client.get("/api/v1/menu", headers=headers)
    assert response.status_code == 200, response.get_json()
    sections = response.get_json()["data"]
    assert len(sections) == 2
    names = {section["category_name"] for section in sections}
    assert "Starters" in names
    assert "Beverages" in names
    all_items = [row for section in sections for row in section["items"]]
    assert len(all_items) == 2
    assert all(row["is_menu"] for row in all_items)


def test_menu_veg_filter(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Grill")
    _item(client, headers, cat_id, "Veg Burger", is_menu=True, is_veg=True)
    _item(client, headers, cat_id, "Chicken Grill", is_menu=True, is_veg=False)

    veg_only = client.get("/api/v1/menu", headers=headers, query_string={"is_veg": "true"})
    assert veg_only.status_code == 200
    items = [row for section in veg_only.get_json()["data"] for row in section["items"]]
    assert len(items) == 1
    assert items[0]["name"] == "Veg Burger"


def test_menu_isolation_across_tenants(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, owner_a, "Tenant A Menu")
    _item(client, owner_a, cat_id, "Tenant A Special", is_menu=True, is_veg=False)

    menu_b = client.get("/api/v1/menu", headers=owner_b).get_json()["data"]
    names = [row["name"] for section in menu_b for row in section["items"]]
    assert "Tenant A Special" not in names


def test_update_item_menu_fields_audited(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Desserts")
    item = _item(client, headers, cat_id, "Ice Cream")

    updated = client.put(
        f"/api/v1/items/{item['id']}",
        headers=headers,
        json={"is_menu": True, "is_veg": True},
    )
    assert updated.status_code == 200, updated.get_json()
    body = updated.get_json()["data"]
    assert body["is_menu"] is True
    assert body["is_veg"] is True

    logs = client.get(
        "/api/v1/audit-logs",
        headers=headers,
        query_string={"entity_type": "ITEM", "per_page": 20},
    ).get_json()["data"]
    assert any(row["action"] == "ITEM_UPDATED" for row in logs)
