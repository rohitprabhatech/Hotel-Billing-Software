"""Sprint BIZ-41 — bakery batch expiry + wastage on finished goods."""

from datetime import date, timedelta

from tests.conftest import login


def _switch(client, headers, business_type="bakery_sweet"):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Bake Batch"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "80",
        "gst_percentage": "0",
        "stock_quantity": "0",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _recipe(client, headers, finished_id, ingredient_id, *, qty="1"):
    response = client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": finished_id,
            "yield_quantity": 1,
            "ingredients": [{"ingredient_item_id": ingredient_id, "quantity": qty}],
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_bakery_has_batch_and_wastage_modules(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    assert "batch_expiry" in modules
    assert "wastage" in modules
    assert "production" in modules


def test_bakery_expiry_alias_and_receive_batch(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    cake = _item(
        client,
        owner,
        cat_id,
        "Batch Cake",
        tracks_batches=True,
        block_expired_batches=True,
        stock_quantity="0",
    )
    soon = (date.today() + timedelta(days=2)).isoformat()
    created = client.post(
        "/api/v1/batches",
        headers=owner,
        json={
            "item_id": cake["id"],
            "quantity": "6",
            "expiry_date": soon,
            "batch_code": "BK-SOON",
        },
    )
    assert created.status_code == 201, created.get_json()

    report = client.get("/api/v1/bakery/expiry", headers=owner, query_string={"within_days": 7})
    assert report.status_code == 200, report.get_json()
    assert report.get_json()["success"] is True
    assert any(row["batch_code"] == "BK-SOON" for row in report.get_json()["data"]["expiring"])


def test_production_creates_batch_when_fg_tracks_batches(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner, "Prod Batch")
    pastry = _item(
        client,
        owner,
        cat_id,
        "Cream Roll",
        tracks_batches=True,
        block_expired_batches=True,
        stock_quantity="0",
    )
    cream = _item(client, owner, cat_id, "Cream", stock_quantity="20", tracks_batches=False)
    recipe = _recipe(client, owner, pastry["id"], cream["id"], qty="2")

    missing = client.post(
        "/api/v1/productions",
        headers=owner,
        json={"recipe_id": recipe["id"], "quantity": "2"},
    )
    assert missing.status_code == 400, missing.get_json()

    expiry = (date.today() + timedelta(days=4)).isoformat()
    produced = client.post(
        "/api/v1/productions",
        headers=owner,
        json={
            "recipe_id": recipe["id"],
            "quantity": "2",
            "expiry_date": expiry,
            "batch_code": "ROLL-A",
        },
    )
    assert produced.status_code == 201, produced.get_json()
    body = produced.get_json()["data"]
    assert body["finished_batch_code"] == "ROLL-A"
    assert body["expiry_date"] == expiry

    pastry_stock = client.get(f"/api/v1/items/{pastry['id']}", headers=owner).get_json()["data"]
    cream_stock = client.get(f"/api/v1/items/{cream['id']}", headers=owner).get_json()["data"]
    assert pastry_stock["stock_quantity"] == 2.0
    assert cream_stock["stock_quantity"] == 16.0

    batches = client.get(
        "/api/v1/batches",
        headers=owner,
        query_string={"item_id": pastry["id"]},
    )
    assert batches.status_code == 200
    assert any(row["batch_code"] == "ROLL-A" for row in batches.get_json()["data"])


def test_bakery_expired_batch_not_sellable(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    cat_id = _category(client, owner, "Sell Expiry")
    bun = _item(
        client,
        owner,
        cat_id,
        "Sweet Bun",
        tracks_batches=True,
        block_expired_batches=True,
        stock_quantity="0",
        price="40",
    )
    past = (date.today() - timedelta(days=1)).isoformat()
    future = (date.today() + timedelta(days=10)).isoformat()
    client.post(
        "/api/v1/batches",
        headers=owner,
        json={"item_id": bun["id"], "quantity": "5", "expiry_date": past, "batch_code": "OLD"},
    )
    client.post(
        "/api/v1/batches",
        headers=owner,
        json={"item_id": bun["id"], "quantity": "2", "expiry_date": future, "batch_code": "NEW"},
    )

    blocked = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"payment_method": "cash", "items": [{"item_id": bun["id"], "quantity": "3"}]},
    )
    assert blocked.status_code == 400, blocked.get_json()

    ok = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"payment_method": "cash", "items": [{"item_id": bun["id"], "quantity": "1"}]},
    )
    assert ok.status_code == 201, ok.get_json()


def test_wastage_consumes_expired_batches_fefo(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner, "Waste Batch")
    cookie = _item(
        client,
        owner,
        cat_id,
        "Cookie Pack",
        tracks_batches=True,
        stock_quantity="0",
    )
    past = (date.today() - timedelta(days=2)).isoformat()
    client.post(
        "/api/v1/batches",
        headers=owner,
        json={
            "item_id": cookie["id"],
            "quantity": "4",
            "expiry_date": past,
            "batch_code": "EXP-W",
        },
    )

    wasted = client.post(
        "/api/v1/wastage",
        headers=owner,
        json={
            "item_id": cookie["id"],
            "quantity": "3",
            "reason": "Expired morning batch",
            "category": "Expired",
        },
    )
    assert wasted.status_code == 201, wasted.get_json()

    item = client.get(f"/api/v1/items/{cookie['id']}", headers=owner).get_json()["data"]
    assert item["stock_quantity"] == 1.0
    batches = client.get(
        "/api/v1/batches",
        headers=owner,
        query_string={"item_id": cookie["id"]},
    ).get_json()["data"]
    match = next(row for row in batches if row["batch_code"] == "EXP-W")
    assert float(match["quantity"]) == 1.0


def test_bakery_adjust_stock_requires_reason(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner, "Adj Bake")
    item = _item(client, owner, cat_id, "Plain FG", stock_quantity="5", tracks_batches=False)
    missing = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": "-1"},
    )
    assert missing.status_code == 400, missing.get_json()
    ok = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": "-1", "reason": "Sample tray"},
    )
    assert ok.status_code == 200, ok.get_json()
