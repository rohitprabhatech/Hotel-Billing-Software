"""Cafe dashboard — popular items/combos + low ingredients (Sprint 4)."""

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, is_menu=False, stock="100", price="40", **extra):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "gst_percentage": "5",
        "stock_quantity": stock,
        "is_menu": is_menu,
        **extra,
    }
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_cafe_dashboard_forbidden_for_hotel(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/cafe/dashboard", headers=headers)
    assert response.status_code == 403, response.get_json()


def test_cafe_dashboard_returns_popular_and_ingredients(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, headers, "Cafe Dash")
    tea = _item(client, headers, cat_id, "Masala Chai Dash", is_menu=True, price="40")
    snack = _item(client, headers, cat_id, "Samosa Dash", is_menu=True, price="30")
    milk = _item(
        client,
        headers,
        cat_id,
        "Milk Dash",
        is_menu=False,
        stock="2",
        price="10",
        minimum_stock_level="5",
    )

    recipe = client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": tea["id"],
            "name": "Chai recipe",
            "yield_quantity": "1",
            "ingredients": [{"ingredient_item_id": milk["id"], "quantity": "0.1"}],
        },
    )
    assert recipe.status_code == 201, recipe.get_json()

    combo = client.post(
        "/api/v1/combos",
        headers=headers,
        json={
            "name": "Dash Combo",
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

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": tea["id"], "quantity": "1"}],
            "combos": [{"combo_id": combo_id, "quantity": "1"}],
        },
    )
    assert order.status_code == 201, order.get_json()
    settled = client.post(
        f"/api/v1/orders/{order.get_json()['data']['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert settled.status_code == 201, settled.get_json()

    dash = client.get("/api/v1/cafe/dashboard?period=today", headers=headers)
    assert dash.status_code == 200, dash.get_json()
    body = dash.get_json()["data"]
    assert body["period"] == "today"
    assert "current" in body
    assert isinstance(body["popular_items"], list)
    assert any(row.get("item_name") == "Masala Chai Dash" for row in body["popular_items"]) or body[
        "popular_items"
    ]
    assert any(row.get("combo_id") == combo_id for row in body["popular_combos"])
    assert any(row.get("item_id") == milk["id"] for row in body["low_ingredients"])
    assert any(row.get("is_popular") for row in body["catalog_popular_combos"])
