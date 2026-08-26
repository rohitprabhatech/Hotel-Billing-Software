"""Sprint BIZ-40 — bakery production runs (ingredient down, FG up)."""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Bake Cat"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, stock="100", price="50"):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "gst_percentage": "0",
        "stock_quantity": stock,
        "uom": "pcs",
    }
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _recipe(client, headers, finished_id, ingredients, *, yield_quantity=1):
    response = client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": finished_id,
            "name": "Bake BOM",
            "yield_quantity": yield_quantity,
            "ingredients": [
                {"ingredient_item_id": row["id"], "quantity": row["qty"]}
                for row in ingredients
            ],
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_restaurant_production_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/productions", headers=owner).status_code == 403


def test_production_consumes_ingredients_and_increases_fg(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner)
    cake = _item(client, owner, cat_id, "Chocolate Cake", stock="5", price="400")
    flour = _item(client, owner, cat_id, "Flour", stock="100")
    sugar = _item(client, owner, cat_id, "Sugar", stock="50")
    recipe = _recipe(
        client,
        owner,
        cake["id"],
        [{"id": flour["id"], "qty": "2"}, {"id": sugar["id"], "qty": "1"}],
        yield_quantity=1,
    )

    produced = client.post(
        "/api/v1/productions",
        headers=owner,
        json={"recipe_id": recipe["id"], "quantity": "3", "notes": "Morning batch"},
    )
    assert produced.status_code == 201, produced.get_json()
    body = produced.get_json()["data"]
    assert body["run_number"].startswith("PR-")
    assert body["quantity"] == 3.0
    assert body["finished_item_id"] == cake["id"]
    assert len(body["items"]) == 2

    cake_stock = client.get(f"/api/v1/items/{cake['id']}", headers=owner).get_json()["data"]
    flour_stock = client.get(f"/api/v1/items/{flour['id']}", headers=owner).get_json()["data"]
    sugar_stock = client.get(f"/api/v1/items/{sugar['id']}", headers=owner).get_json()["data"]
    assert cake_stock["stock_quantity"] == 8.0  # 5 + 3
    assert flour_stock["stock_quantity"] == 94.0  # 100 - 6
    assert sugar_stock["stock_quantity"] == 47.0  # 50 - 3

    movements = client.get(
        "/api/v1/stock-movements",
        headers=owner,
        query_string={"item_id": flour["id"], "per_page": 5},
    ).get_json()["data"]
    assert any(row["source"] == "PRODUCTION" for row in movements)

    listing = client.get("/api/v1/productions", headers=owner)
    assert listing.status_code == 200, listing.get_json()
    assert listing.get_json()["success"] is True
    assert any(row["id"] == body["id"] for row in listing.get_json()["data"])


def test_production_blocks_insufficient_ingredient(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Scarce Bake")
    bun = _item(client, owner, cat_id, "Bun", stock="0")
    yeast = _item(client, owner, cat_id, "Yeast", stock="0.5")
    recipe = _recipe(
        client,
        owner,
        bun["id"],
        [{"id": yeast["id"], "qty": "1"}],
    )
    denied = client.post(
        "/api/v1/productions",
        headers=owner,
        json={"recipe_id": recipe["id"], "quantity": "2"},
    )
    assert denied.status_code == 400, denied.get_json()


def test_bakery_sale_deducts_finished_goods_not_ingredients(client):
    """With production module on, POS sell depletes FG stock (ingredients already baked)."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Sell Bake")
    pastry = _item(client, owner, cat_id, "Pastry", stock="10", price="100")
    butter = _item(client, owner, cat_id, "Butter", stock="80")
    recipe = _recipe(
        client,
        owner,
        pastry["id"],
        [{"id": butter["id"], "qty": "0.5"}],
    )
    assert recipe["id"]

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": pastry["id"], "quantity": "2"}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()

    pastry_stock = client.get(f"/api/v1/items/{pastry['id']}", headers=owner).get_json()["data"]
    butter_stock = client.get(f"/api/v1/items/{butter['id']}", headers=owner).get_json()["data"]
    assert pastry_stock["stock_quantity"] == 8.0
    assert butter_stock["stock_quantity"] == 80.0  # unchanged


def test_production_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "bakery_sweet")
    _switch(client, owner_b, "bakery_sweet")
    cat_id = _category(client, owner_a, "Iso Bake")
    cake = _item(client, owner_a, cat_id, "Iso Cake", stock="2")
    flour = _item(client, owner_a, cat_id, "Iso Flour", stock="20")
    recipe = _recipe(client, owner_a, cake["id"], [{"id": flour["id"], "qty": "1"}])
    created = client.post(
        "/api/v1/productions",
        headers=owner_a,
        json={"recipe_id": recipe["id"], "quantity": "1"},
    )
    assert created.status_code == 201, created.get_json()
    run_id = created.get_json()["data"]["id"]

    foreign = client.get(f"/api/v1/productions/{run_id}", headers=owner_b)
    assert foreign.status_code == 404, foreign.get_json()


def test_billing_cannot_create_production(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Perm Bake")
    cookie = _item(client, owner, cat_id, "Cookie", stock="1")
    choc = _item(client, owner, cat_id, "Choc Chip", stock="10")
    recipe = _recipe(client, owner, cookie["id"], [{"id": choc["id"], "qty": "0.2"}])

    denied = client.post(
        "/api/v1/productions",
        headers=billing,
        json={"recipe_id": recipe["id"], "quantity": "1"},
    )
    assert denied.status_code == 403, denied.get_json()

    ok = client.post(
        "/api/v1/productions",
        headers=manager,
        json={"recipe_id": recipe["id"], "quantity": "1"},
    )
    assert ok.status_code == 201, ok.get_json()
    assert Decimal(str(ok.get_json()["data"]["quantity"])) == Decimal("1")
