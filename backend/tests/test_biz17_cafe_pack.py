"""Sprint BIZ-17 — cafe add-ons, combos, and quick POS."""

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, is_menu=False, stock="100", price="120"):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "gst_percentage": "5",
        "stock_quantity": stock,
        "is_menu": is_menu,
    }
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_cafe_tenant_has_addons_module(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert response.status_code == 200, response.get_json()
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "addons_combos" in enabled


def test_restaurant_tenant_lacks_addons_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "addons_combos" not in enabled


def test_addons_api_forbidden_for_restaurant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/menu/addons", headers=headers)
    assert response.status_code == 403, response.get_json()
    assert response.get_json()["error"]["code"] == "FORBIDDEN"


def test_create_combo_and_order_with_addons_settles(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, headers, "Cafe Drinks")
    tea = _item(client, headers, cat_id, "Masala Chai", is_menu=True, price="40")
    snack = _item(client, headers, cat_id, "Samosa", is_menu=True, price="30")

    addon_group = client.post(
        "/api/v1/menu/addons",
        headers=headers,
        json={
            "menu_item_id": tea["id"],
            "name": "Milk",
            "addons": [
                {"name": "Extra Strong", "extra_price": "10"},
                {"name": "Regular", "extra_price": "0", "is_default": True},
            ],
        },
    )
    assert addon_group.status_code == 201, addon_group.get_json()
    extra_addon_id = addon_group.get_json()["data"]["addons"][0]["id"]

    combo = client.post(
        "/api/v1/combos",
        headers=headers,
        json={
            "name": "Chai Samosa Combo",
            "combo_price": "60",
            "is_popular": True,
            "items": [
                {"item_id": tea["id"], "quantity": "1"},
                {"item_id": snack["id"], "quantity": "1"},
            ],
        },
    )
    assert combo.status_code == 201, combo.get_json()
    combo_id = combo.get_json()["data"]["id"]

    catalog = client.get("/api/v1/cafe/pos-catalog", headers=headers)
    assert catalog.status_code == 200, catalog.get_json()
    body = catalog.get_json()["data"]
    assert len(body["popular_combos"]) >= 1
    assert any(row["id"] == tea["id"] for row in body["menu_items"])

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": tea["id"], "quantity": "1", "addon_ids": [extra_addon_id]}],
            "combos": [{"combo_id": combo_id, "quantity": "1"}],
        },
    )
    assert order.status_code == 201, order.get_json()
    order_data = order.get_json()["data"]
    assert len(order_data["items"]) == 3
    assert float(order_data["grand_total"]) > 0

    addon_line = next(row for row in order_data["items"] if row["addons"])
    assert addon_line["addons"][0]["addon_name"] == "Extra Strong"
    assert float(addon_line["unit_price"]) == 50.0

    settled = client.post(
        f"/api/v1/orders/{order_data['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert settled.status_code == 201, settled.get_json()
    assert settled.get_json()["data"]["bills"][0]["bill_number"]


def test_restaurant_cannot_create_combo_order(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Resto")
    item = _item(client, headers, cat_id, "Soup", is_menu=True)

    response = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "combos": [{"combo_id": "fake-combo-id", "quantity": "1"}],
        },
    )
    assert response.status_code == 403, response.get_json()


def test_combo_expands_to_component_lines(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, headers, "Combo Cat")
    a = _item(client, headers, cat_id, "Coffee", is_menu=True, price="50")
    b = _item(client, headers, cat_id, "Cookie", is_menu=True, price="30")

    combo = client.post(
        "/api/v1/combos",
        headers=headers,
        json={
            "name": "Coffee Cookie",
            "combo_price": "70",
            "items": [
                {"item_id": a["id"], "quantity": "1"},
                {"item_id": b["id"], "quantity": "1"},
            ],
        },
    ).get_json()["data"]

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "combos": [{"combo_id": combo["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    combo_lines = [row for row in order["items"] if row["combo_id"]]
    assert len(combo_lines) == 2
    catalog_total = sum(float(row["unit_price"]) * float(row["quantity"]) for row in combo_lines)
    assert abs(catalog_total - 70.0) < 0.05
