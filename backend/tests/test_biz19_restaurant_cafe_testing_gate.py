"""Sprint BIZ-19 — restaurant & cafe F&B testing gate.

Integration, isolation, permission, audit, stock, billing, and contract checks
across BIZ-11 … BIZ-18.

Run full phase gate from backend/:
  python -m pytest tests/test_biz11_restaurant_foundation.py tests/test_biz12_table_management.py
    tests/test_biz13_order_channels.py tests/test_biz14_kot_kitchen_dashboard.py
    tests/test_biz15_restaurant_billing.py tests/test_biz16_recipe_ingredient_stock.py
    tests/test_biz17_cafe_pack.py tests/test_biz18_fb_reports_wastage.py
    tests/test_biz19_restaurant_cafe_testing_gate.py -q
"""

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, is_menu=False, stock="50", price="200"):
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


def _table(client, headers, code):
    response = client.post("/api/v1/tables", headers=headers, json={"code": code, "capacity": 4})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def test_gate_fb_cross_tenant_isolation_matrix(client):
    """Tables, orders, KOTs, recipes, and wastage must not leak across tenants."""
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    cat_a = _category(client, owner_a, "Gate-FB-Iso")
    menu_a = _item(client, owner_a, cat_a, "Gate Menu", is_menu=True)
    ing_a = _item(client, owner_a, cat_a, "Gate Ingredient", stock="20")
    table_a = _table(client, owner_a, "G-ISO-1")

    recipe = client.post(
        "/api/v1/recipes",
        headers=owner_a,
        json={
            "menu_item_id": menu_a["id"],
            "ingredients": [{"ingredient_item_id": ing_a["id"], "quantity": "0.5"}],
        },
    )
    assert recipe.status_code == 201, recipe.get_json()
    recipe_id = recipe.get_json()["data"]["id"]

    order = client.post(
        "/api/v1/orders",
        headers=owner_a,
        json={
            "channel": "dine_in",
            "dining_table_id": table_a["id"],
            "items": [{"item_id": menu_a["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    kot = client.post(f"/api/v1/orders/{order['id']}/kot", headers=owner_a).get_json()["data"]

    wastage = client.post(
        "/api/v1/wastage",
        headers=owner_a,
        json={"item_id": ing_a["id"], "quantity": "1", "reason": "Gate spoilage"},
    )
    assert wastage.status_code == 201, wastage.get_json()
    wastage_id = wastage.get_json()["data"]["id"]

    probes = [
        f"/api/v1/tables/{table_a['id']}",
        f"/api/v1/orders/{order['id']}",
        f"/api/v1/kots/{kot['id']}",
        f"/api/v1/recipes/{recipe_id}",
        f"/api/v1/wastage/{wastage_id}",
    ]
    for path in probes:
        response = client.get(path, headers=owner_b)
        assert response.status_code == 404, (path, response.get_json())

    queue_b = client.get("/api/v1/kots/kitchen/queue", headers=owner_b).get_json()["data"]
    assert all(row["id"] != kot["id"] for row in queue_b)


def test_gate_restaurant_dine_in_to_settle_e2e(client):
    """Table → order → KOT → kitchen ready → settle → stock + table release."""
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Gate-E2E")
    menu_item = _item(client, headers, cat_id, "Gate E2E Dish", is_menu=True, stock="10")
    ingredient = _item(client, headers, cat_id, "Gate E2E Ing", stock="100")
    table = _table(client, headers, "G-E2E-1")

    client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": menu_item["id"],
            "ingredients": [{"ingredient_item_id": ingredient["id"], "quantity": "2"}],
        },
    )

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "dine_in",
            "dining_table_id": table["id"],
            "items": [{"item_id": menu_item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    kot = client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers).get_json()["data"]
    client.patch(
        f"/api/v1/kots/{kot['id']}/status",
        headers=headers,
        json={"status": "ready"},
    )

    settled = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash", "service_charge": "10"},
    )
    assert settled.status_code == 201, settled.get_json()
    body = settled.get_json()["data"]
    assert body["order"]["status"] == "BILLED"
    assert len(body["bills"]) == 1

    table_state = client.get(f"/api/v1/tables/{table['id']}", headers=headers).get_json()["data"]
    assert table_state["status"] == "available"

    menu_stock = client.get(f"/api/v1/items/{menu_item['id']}", headers=headers).get_json()["data"]
    ing_stock = client.get(f"/api/v1/items/{ingredient['id']}", headers=headers).get_json()["data"]
    assert menu_stock["stock_quantity"] == 10.0
    assert ing_stock["stock_quantity"] == 98.0

    fb = client.get("/api/v1/reports/fb", headers=headers)
    assert fb.status_code == 200, fb.get_json()
    channels = {row["channel"] for row in fb.get_json()["data"]["channel_wise"]}
    assert "dine_in" in channels


def test_gate_cafe_combo_addon_settle_e2e(client):
    """Cafe tenant: combo + add-on order settles to bill with correct pricing."""
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, headers, "Gate-Cafe")
    tea = _item(client, headers, cat_id, "Gate Chai", is_menu=True, price="40")
    snack = _item(client, headers, cat_id, "Gate Snack", is_menu=True, price="30")

    addon_group = client.post(
        "/api/v1/menu/addons",
        headers=headers,
        json={
            "menu_item_id": tea["id"],
            "name": "Strength",
            "addons": [{"name": "Extra strong", "extra_price": "10"}],
        },
    ).get_json()["data"]
    addon_id = addon_group["addons"][0]["id"]

    combo = client.post(
        "/api/v1/combos",
        headers=headers,
        json={
            "name": "Gate Combo",
            "combo_price": "60",
            "items": [
                {"item_id": tea["id"], "quantity": "1"},
                {"item_id": snack["id"], "quantity": "1"},
            ],
        },
    ).get_json()["data"]

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": tea["id"], "quantity": "1", "addon_ids": [addon_id]}],
            "combos": [{"combo_id": combo["id"], "quantity": "1"}],
        },
    ).get_json()["data"]
    assert len(order["items"]) == 3

    settled = client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert settled.status_code == 201, settled.get_json()
    assert settled.get_json()["data"]["bills"][0]["order_id"] == order["id"]


def test_gate_fb_permission_matrix(client):
    """F&B role boundaries: billing ops vs manager back-office."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    assert client.get("/api/v1/orders", headers=owner).status_code == 200
    assert client.get("/api/v1/orders", headers=manager).status_code == 200
    assert client.get("/api/v1/orders", headers=billing).status_code == 200

    assert client.get("/api/v1/kots/kitchen/queue", headers=billing).status_code == 200
    assert client.get("/api/v1/reports/fb", headers=manager).status_code == 200
    assert client.get("/api/v1/reports/fb", headers=billing).status_code == 403

    assert client.get("/api/v1/wastage", headers=manager).status_code == 200
    assert client.get("/api/v1/wastage", headers=billing).status_code == 200

    assert client.get("/api/v1/recipes", headers=manager).status_code == 200
    assert client.get("/api/v1/recipes", headers=billing).status_code == 200

    cafe_billing = login(client, "billing@hotelb.com", "Billing@12345")
    assert client.get("/api/v1/wastage", headers=cafe_billing).status_code == 403
    assert client.get("/api/v1/recipes", headers=cafe_billing).status_code == 403

    assert client.get("/api/v1/menu/addons", headers=owner).status_code == 403
    cafe_owner = login(client, "owner@hotelb.com", "Owner@12345")
    assert client.get("/api/v1/menu/addons", headers=cafe_owner).status_code == 200


def test_gate_fb_module_matrix_restaurant_vs_cafe(client):
    """Industry modules differ: restaurant wastage, cafe addons, neither on clothing."""
    rest = login(client, "owner@hotela.com", "Owner@12345")
    cafe = login(client, "owner@hotelb.com", "Owner@12345")

    rest_modules = client.get("/api/v1/tenants/me/modules", headers=rest).get_json()["data"]["enabled_modules"]
    cafe_modules = client.get("/api/v1/tenants/me/modules", headers=cafe).get_json()["data"]["enabled_modules"]

    assert "wastage" in rest_modules
    assert "wastage" in cafe_modules
    assert "addons_combos" not in rest_modules
    assert "addons_combos" in cafe_modules
    assert "order_channels" in rest_modules
    assert "order_channels" in cafe_modules

    client.put("/api/v1/tenants/me", headers=rest, json={"business_type": "clothing"})
    clothing_modules = client.get("/api/v1/tenants/me/modules", headers=rest).get_json()["data"]["enabled_modules"]
    assert "order_channels" not in clothing_modules
    assert "kot" not in clothing_modules


def test_gate_split_bill_and_insufficient_stock(client):
    """Split bill totals match; insufficient stock blocks settle."""
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Gate-Split")
    item_a = _item(client, headers, cat_id, "Gate Split A", price="300", stock="50")
    item_b = _item(client, headers, cat_id, "Gate Split B", price="200", stock="50")
    low = _item(client, headers, cat_id, "Gate Low Stock", stock="1")

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [
                {"item_id": item_a["id"], "quantity": "1"},
                {"item_id": item_b["id"], "quantity": "1"},
            ],
        },
    ).get_json()["data"]
    line_a, line_b = order["items"][0]["id"], order["items"][1]["id"]

    split = client.post(
        "/api/v1/bills/split",
        headers=headers,
        json={
            "order_id": order["id"],
            "splits": [
                {"order_item_ids": [line_a], "payment_method": "cash"},
                {"order_item_ids": [line_b], "payment_method": "online"},
            ],
        },
    )
    assert split.status_code == 201, split.get_json()
    assert len(split.get_json()["data"]["bills"]) == 2

    low_order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": low["id"], "quantity": "5"}],
        },
    ).get_json()["data"]
    denied = client.post(
        f"/api/v1/orders/{low_order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )
    assert denied.status_code == 400, denied.get_json()
    assert denied.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"


def test_gate_wastage_stock_and_fb_report(client):
    """Wastage deducts stock; FB report includes wastage summary."""
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Gate-Wastage")
    ingredient = _item(client, headers, cat_id, "Gate Tomato", stock="10")

    created = client.post(
        "/api/v1/wastage",
        headers=headers,
        json={"item_id": ingredient["id"], "quantity": "2", "reason": "Spoiled"},
    )
    assert created.status_code == 201, created.get_json()

    item_state = client.get(f"/api/v1/items/{ingredient['id']}", headers=headers).get_json()["data"]
    assert item_state["stock_quantity"] == 8.0

    movements = client.get(
        "/api/v1/stock-movements",
        headers=headers,
        query_string={"item_id": ingredient["id"], "source": "WASTAGE"},
    ).get_json()["data"]
    assert len(movements) >= 1

    fb = client.get("/api/v1/reports/fb", headers=headers).get_json()["data"]
    assert fb["wastage"]["entry_count"] >= 1
    assert fb["wastage"]["total_quantity"] >= 2.0


def test_gate_fb_audit_spot_check(client):
    """Key F&B mutations appear in owner audit log."""
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Gate-Audit")
    item = _item(client, headers, cat_id, "Gate Audit Dish", is_menu=True)
    table = _table(client, headers, "G-AUD-1")

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "dine_in",
            "dining_table_id": table["id"],
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]
    client.post(f"/api/v1/orders/{order['id']}/kot", headers=headers)
    client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )

    actions = {row["action"] for row in _audit_actions(client, headers)}
    assert "CREATE_ORDER" in actions
    assert "CREATE_KOT" in actions


def test_gate_fb_api_response_contracts(client):
    """Standard success envelope on F&B list endpoints."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    cafe = login(client, "owner@hotelb.com", "Owner@12345")

    restaurant_lists = [
        "/api/v1/tables",
        "/api/v1/orders",
        "/api/v1/kots/kitchen/queue",
        "/api/v1/recipes",
        "/api/v1/wastage",
        "/api/v1/menu",
    ]
    for path in restaurant_lists:
        response = client.get(path, headers=owner)
        assert response.status_code == 200, (path, response.get_json())
        body = response.get_json()
        assert body["success"] is True
        assert "data" in body

    fb = client.get("/api/v1/reports/fb", headers=owner)
    assert fb.status_code == 200, fb.get_json()
    fb_body = fb.get_json()
    assert fb_body["success"] is True
    for key in ("channel_wise", "table_wise", "wastage", "metrics"):
        assert key in fb_body["data"]

    combos = client.get("/api/v1/combos", headers=cafe)
    assert combos.status_code == 200, combos.get_json()
    assert combos.get_json()["success"] is True


def test_gate_manager_fb_ops_path(client):
    """Manager can run orders, KOT, wastage, and F&B reports."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    cat_id = _category(client, owner, "Gate-Mgr-FB")
    item = _item(client, owner, cat_id, "Gate Mgr Dish", is_menu=True, stock="20")

    order = client.post(
        "/api/v1/orders",
        headers=manager,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    )
    assert order.status_code == 201, order.get_json()

    kot = client.post(
        f"/api/v1/orders/{order.get_json()['data']['id']}/kot",
        headers=manager,
    )
    assert kot.status_code == 201, kot.get_json()

    wastage = client.post(
        "/api/v1/wastage",
        headers=manager,
        json={"item_id": item["id"], "quantity": "1", "reason": "Sample"},
    )
    assert wastage.status_code == 201, wastage.get_json()

    report = client.get("/api/v1/reports/fb", headers=manager)
    assert report.status_code == 200, report.get_json()


def test_gate_biz11_through_18_smoke(client):
    """Baseline F&B sprint tests still reachable (module + menu smoke)."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner)
    assert modules.status_code == 200
    enabled = modules.get_json()["data"]["enabled_modules"]
    assert "restaurant_menu" in enabled
    assert "table_management" in enabled
    assert "kot" in enabled
    assert "kitchen" in enabled
    assert "recipe" in enabled
    assert "wastage" in enabled

    menu = client.get("/api/v1/menu", headers=owner)
    assert menu.status_code == 200, menu.get_json()
    assert isinstance(menu.get_json()["data"], list)
