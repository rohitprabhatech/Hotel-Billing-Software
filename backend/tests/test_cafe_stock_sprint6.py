"""Sprint 6: cafe addon linked_item stock + hotel recipe regression."""

from decimal import Decimal

from app.models.item import Item
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


def test_cafe_addon_linked_item_deducts_on_settle(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, headers, "Sprint6 Linked")
    tea = _item(client, headers, cat_id, "Chai S6", is_menu=True, stock="50", price="40")
    milk = _item(client, headers, cat_id, "Extra Milk S6", is_menu=False, stock="20", price="5")

    addon_group = client.post(
        "/api/v1/menu/addons",
        headers=headers,
        json={
            "menu_item_id": tea["id"],
            "name": "Milk options",
            "addons": [
                {
                    "name": "Extra Milk",
                    "extra_price": "10",
                    "linked_item_id": milk["id"],
                }
            ],
        },
    )
    assert addon_group.status_code == 201, addon_group.get_json()
    addon_id = addon_group.get_json()["data"]["addons"][0]["id"]
    assert addon_group.get_json()["data"]["addons"][0]["linked_item_id"] == milk["id"]

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": tea["id"], "quantity": "2", "addon_ids": [addon_id]}],
        },
    )
    assert order.status_code == 201, order.get_json()
    order_id = order.get_json()["data"]["id"]

    settled = client.post(
        f"/api/v1/orders/{order_id}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert settled.status_code == 201, settled.get_json()

    milk_row = Item.query.filter_by(id=milk["id"]).first()
    # 2× line qty of linked milk
    assert Decimal(str(milk_row.stock_quantity)) == Decimal("18")


def test_cafe_addon_linked_insufficient_blocks_settle(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, headers, "Sprint6 Low Link")
    tea = _item(client, headers, cat_id, "Chai Low S6", is_menu=True, stock="50", price="40")
    syrup = _item(client, headers, cat_id, "Syrup Low S6", is_menu=False, stock="1", price="5")

    addon_id = client.post(
        "/api/v1/menu/addons",
        headers=headers,
        json={
            "menu_item_id": tea["id"],
            "name": "Syrup",
            "addons": [
                {"name": "Vanilla", "extra_price": "5", "linked_item_id": syrup["id"]},
            ],
        },
    ).get_json()["data"]["addons"][0]["id"]

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": tea["id"], "quantity": "3", "addon_ids": [addon_id]}],
        },
    )
    assert order.status_code == 201, order.get_json()

    settled = client.post(
        f"/api/v1/orders/{order.get_json()['data']['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert settled.status_code in (400, 409), settled.get_json()
    assert settled.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"
    syrup_row = Item.query.filter_by(id=syrup["id"]).first()
    assert Decimal(str(syrup_row.stock_quantity)) == Decimal("1")


def test_hotel_recipe_settle_unaffected_by_addon_stock_rule(client):
    """Hotel regression: recipe ingredient deduct still works; no addon module."""
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Hotel S6 Recipe")
    dish = _item(client, headers, cat_id, "Soup S6", is_menu=True, stock="10", price="80")
    stock_before_dish = Decimal(str(dish["stock_quantity"]))
    veg = _item(client, headers, cat_id, "Veg Stock S6", is_menu=False, stock="30", price="10")

    recipe = client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": dish["id"],
            "name": "Soup recipe",
            "yield_quantity": "1",
            "ingredients": [{"ingredient_item_id": veg["id"], "quantity": "2"}],
        },
    )
    assert recipe.status_code == 201, recipe.get_json()

    # Hotel cannot create addon groups
    blocked = client.post(
        "/api/v1/menu/addons",
        headers=headers,
        json={
            "menu_item_id": dish["id"],
            "name": "Blocked",
            "addons": [{"name": "X", "extra_price": "0"}],
        },
    )
    assert blocked.status_code == 403, blocked.get_json()

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": dish["id"], "quantity": "1"}],
        },
    )
    assert order.status_code == 201, order.get_json()
    settled = client.post(
        f"/api/v1/orders/{order.get_json()['data']['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert settled.status_code == 201, settled.get_json()

    veg_row = Item.query.filter_by(id=veg["id"]).first()
    dish_row = Item.query.filter_by(id=dish["id"]).first()
    assert Decimal(str(veg_row.stock_quantity)) == Decimal("28")
    # Recipe expand skips finished-goods deduct
    assert Decimal(str(dish_row.stock_quantity)) == stock_before_dish
