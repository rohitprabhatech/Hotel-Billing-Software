"""Sprint BIZ-16 — recipes and ingredient stock on settle."""

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, is_menu=False, stock="100", price="250"):
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


def test_create_recipe_and_settle_deducts_ingredients(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Recipe Cat")
    menu_item = _item(client, headers, cat_id, "Paneer Tikka", is_menu=True, stock="10")
    flour = _item(client, headers, cat_id, "Paneer", stock="500")
    spice = _item(client, headers, cat_id, "Masala Mix", stock="200")

    recipe = client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": menu_item["id"],
            "yield_quantity": 1,
            "ingredients": [
                {"ingredient_item_id": flour["id"], "quantity": "0.2"},
                {"ingredient_item_id": spice["id"], "quantity": "0.05"},
            ],
        },
    )
    assert recipe.status_code == 201, recipe.get_json()

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": menu_item["id"], "quantity": "2"}],
        },
    ).get_json()["data"]

    settled = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert settled.status_code == 201, settled.get_json()

    menu_stock = client.get(f"/api/v1/items/{menu_item['id']}", headers=headers).get_json()["data"]
    flour_stock = client.get(f"/api/v1/items/{flour['id']}", headers=headers).get_json()["data"]
    spice_stock = client.get(f"/api/v1/items/{spice['id']}", headers=headers).get_json()["data"]

    assert menu_stock["stock_quantity"] == 10.0
    assert flour_stock["stock_quantity"] == 499.6
    assert spice_stock["stock_quantity"] == 199.9

    movements = client.get(
        "/api/v1/stock-movements",
        headers=headers,
        query_string={"item_id": flour["id"], "per_page": 5},
    ).get_json()["data"]
    assert any(row["source"] == "RECIPE" for row in movements)


def test_settle_blocks_insufficient_ingredient_stock(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Low Ing Cat")
    menu_item = _item(client, headers, cat_id, "Low Ing Dish", is_menu=True, stock=None)
    ingredient = _item(client, headers, cat_id, "Scarce Ingredient", stock="0.1")

    client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": menu_item["id"],
            "ingredients": [{"ingredient_item_id": ingredient["id"], "quantity": "1"}],
        },
    )

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": menu_item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    denied = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert denied.status_code == 400, denied.get_json()
    assert denied.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"


def test_recipe_requires_menu_item(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Non Menu Cat")
    raw_item = _item(client, headers, cat_id, "Raw Only", is_menu=False)
    ingredient = _item(client, headers, cat_id, "Salt", stock="50")

    denied = client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": raw_item["id"],
            "ingredients": [{"ingredient_item_id": ingredient["id"], "quantity": "0.01"}],
        },
    )
    assert denied.status_code == 400, denied.get_json()


def test_recipe_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, owner_a, "Iso Recipe Cat")
    menu_item = _item(client, owner_a, cat_id, "Iso Menu", is_menu=True)
    ingredient = _item(client, owner_a, cat_id, "Iso Ing", stock="20")

    recipe = client.post(
        "/api/v1/recipes",
        headers=owner_a,
        json={
            "menu_item_id": menu_item["id"],
            "ingredients": [{"ingredient_item_id": ingredient["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    denied = client.get(f"/api/v1/recipes/{recipe['id']}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()
