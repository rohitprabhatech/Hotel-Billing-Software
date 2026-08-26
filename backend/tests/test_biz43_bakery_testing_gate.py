"""Sprint BIZ-43 — bakery testing gate.

Regression matrix across BIZ-40 … BIZ-42: production runs, batch/expiry FG,
wastage FEFO, custom cake orders + advances, module matrix, isolation,
permissions, audit, and API contracts.

Run full phase gate from backend/:
  python -m pytest tests/test_biz40_bakery_production.py \\
    tests/test_biz41_bakery_batch_expiry_wastage.py \\
    tests/test_biz42_custom_cake_orders.py \\
    tests/test_biz43_bakery_testing_gate.py -q
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type: str):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Gate Bake"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "50",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _recipe(client, headers, finished_id, ingredients, *, yield_quantity=1):
    response = client.post(
        "/api/v1/recipes",
        headers=headers,
        json={
            "menu_item_id": finished_id,
            "name": "Gate BOM",
            "yield_quantity": yield_quantity,
            "ingredients": [
                {"ingredient_item_id": row["id"], "quantity": row["qty"]}
                for row in ingredients
            ],
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_restaurant_bakery_vertical_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    for path in (
        "/api/v1/productions",
        "/api/v1/custom-orders",
        "/api/v1/bakery/expiry",
        "/api/v1/bakery/cake-orders",
    ):
        assert client.get(path, headers=owner).status_code == 403, path


def test_gate_module_matrix_bakery(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "bakery_sweet")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in (
        "production",
        "recipe",
        "batch_expiry",
        "custom_orders",
        "wastage",
    ):
        assert code in modules, code
    assert "serial_imei" not in modules
    assert "warehouse" not in modules
    assert "order_channels" not in modules


def test_gate_production_ingredient_down_fg_up(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Gate-Prod")
    cake = _item(client, owner, cat_id, "Gate Cake", stock_quantity="2", price="400")
    flour = _item(client, owner, cat_id, "Gate Flour", stock_quantity="40")
    recipe = _recipe(
        client,
        owner,
        cake["id"],
        [{"id": flour["id"], "qty": "2"}],
    )

    produced = client.post(
        "/api/v1/productions",
        headers=owner,
        json={"recipe_id": recipe["id"], "quantity": "3", "notes": "Gate batch"},
    )
    assert produced.status_code == 201, produced.get_json()
    assert produced.get_json()["success"] is True
    body = produced.get_json()["data"]
    assert body["run_number"].startswith("PR-")
    assert body["quantity"] == 3.0

    cake_stock = client.get(f"/api/v1/items/{cake['id']}", headers=owner).get_json()["data"]
    flour_stock = client.get(f"/api/v1/items/{flour['id']}", headers=owner).get_json()["data"]
    assert cake_stock["stock_quantity"] == 5.0
    assert flour_stock["stock_quantity"] == 34.0

    # Bakery sell deducts FG, not ingredients again
    billing = login(client, "billing@hotela.com", "Billing@12345")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": cake["id"], "quantity": "1"}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    cake_after = client.get(f"/api/v1/items/{cake['id']}", headers=owner).get_json()["data"]
    flour_after = client.get(f"/api/v1/items/{flour['id']}", headers=owner).get_json()["data"]
    assert cake_after["stock_quantity"] == 4.0
    assert flour_after["stock_quantity"] == 34.0


def test_gate_production_batch_expiry_and_sell_rules(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Gate-Batch")
    pastry = _item(
        client,
        owner,
        cat_id,
        "Gate Pastry",
        stock_quantity="0",
        tracks_batches=True,
        block_expired_batches=True,
        price="80",
    )
    butter = _item(client, owner, cat_id, "Gate Butter", stock_quantity="30")
    recipe = _recipe(client, owner, pastry["id"], [{"id": butter["id"], "qty": "1"}])

    expiry = (date.today() + timedelta(days=3)).isoformat()
    produced = client.post(
        "/api/v1/productions",
        headers=owner,
        json={
            "recipe_id": recipe["id"],
            "quantity": "4",
            "expiry_date": expiry,
            "batch_code": "GATE-P1",
        },
    )
    assert produced.status_code == 201, produced.get_json()
    assert produced.get_json()["data"]["finished_batch_code"] == "GATE-P1"

    report = client.get("/api/v1/bakery/expiry", headers=owner, query_string={"within_days": 7})
    assert report.status_code == 200, report.get_json()
    assert report.get_json()["success"] is True
    assert any(row["batch_code"] == "GATE-P1" for row in report.get_json()["data"]["expiring"])

    past = (date.today() - timedelta(days=1)).isoformat()
    client.post(
        "/api/v1/batches",
        headers=owner,
        json={
            "item_id": pastry["id"],
            "quantity": "5",
            "expiry_date": past,
            "batch_code": "GATE-OLD",
        },
    )
    blocked = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": pastry["id"], "quantity": "6"}],
        },
    )
    assert blocked.status_code == 400, blocked.get_json()

    ok = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": pastry["id"], "quantity": "2"}],
        },
    )
    assert ok.status_code == 201, ok.get_json()


def test_gate_wastage_and_cake_order_pipeline(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Gate-Waste")
    cookie = _item(
        client,
        owner,
        cat_id,
        "Gate Cookie",
        stock_quantity="0",
        tracks_batches=True,
    )
    past = (date.today() - timedelta(days=2)).isoformat()
    client.post(
        "/api/v1/batches",
        headers=owner,
        json={
            "item_id": cookie["id"],
            "quantity": "5",
            "expiry_date": past,
            "batch_code": "GATE-W",
        },
    )
    wasted = client.post(
        "/api/v1/wastage",
        headers=owner,
        json={
            "item_id": cookie["id"],
            "quantity": "2",
            "reason": "Expired gate batch",
            "category": "Expired",
        },
    )
    assert wasted.status_code == 201, wasted.get_json()
    assert wasted.get_json()["success"] is True

    created = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={
            "order_type": "bakery",
            "title": "Gate Wedding Cake",
            "size": "3 kg",
            "flavor": "Vanilla",
            "customer_name": "Gate Guest",
            "total_amount": "5000",
            "advance_amount": "1000",
            "delivery_at": (datetime.now(timezone.utc) + timedelta(days=1)).replace(tzinfo=None).isoformat(),
        },
    )
    assert created.status_code == 201, created.get_json()
    order = created.get_json()["data"]
    assert order["order_number"].startswith("CO-")
    assert order["remaining_amount"] == 4000.0
    assert Decimal(str(order["advance_paid"])) == Decimal("1000")

    denied_status = client.patch(
        f"/api/v1/custom-orders/{order['id']}/status",
        headers=billing,
        json={"status": "CONFIRMED"},
    )
    assert denied_status.status_code == 403, denied_status.get_json()

    for status in ("CONFIRMED", "IN_PRODUCTION", "READY"):
        updated = client.patch(
            f"/api/v1/custom-orders/{order['id']}/status",
            headers=manager,
            json={"status": status},
        )
        assert updated.status_code == 200, updated.get_json()
        assert updated.get_json()["data"]["status"] == status

    more = client.post(
        f"/api/v1/custom-orders/{order['id']}/advance",
        headers=billing,
        json={"amount": "500", "payment_method": "upi"},
    )
    assert more.status_code == 201, more.get_json()
    assert more.get_json()["data"]["advance_paid"] == 1500.0


def test_gate_permissions_billing_cannot_write_production(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Gate-Perm")
    bun = _item(client, owner, cat_id, "Gate Bun", stock_quantity="1")
    yeast = _item(client, owner, cat_id, "Gate Yeast", stock_quantity="10")
    recipe = _recipe(client, owner, bun["id"], [{"id": yeast["id"], "qty": "0.5"}])

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

    listing = client.get("/api/v1/productions", headers=manager)
    assert listing.status_code == 200, listing.get_json()


def test_gate_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "bakery_sweet")
    _switch(client, owner_b, "bakery_sweet")

    cat_a = _category(client, owner_a, "Gate-Iso-A")
    cake = _item(client, owner_a, cat_a, "Iso Gate Cake", stock_quantity="2")
    flour = _item(client, owner_a, cat_a, "Iso Gate Flour", stock_quantity="10")
    recipe = _recipe(client, owner_a, cake["id"], [{"id": flour["id"], "qty": "1"}])
    produced = client.post(
        "/api/v1/productions",
        headers=owner_a,
        json={"recipe_id": recipe["id"], "quantity": "1"},
    )
    assert produced.status_code == 201, produced.get_json()
    run_id = produced.get_json()["data"]["id"]

    foreign_run = client.get(f"/api/v1/productions/{run_id}", headers=owner_b)
    assert foreign_run.status_code == 404, foreign_run.get_json()

    cake_order = client.post(
        "/api/v1/custom-orders",
        headers=owner_a,
        json={"title": "Iso Gate Order", "total_amount": "800", "advance_amount": "100"},
    )
    assert cake_order.status_code == 201, cake_order.get_json()
    oid = cake_order.get_json()["data"]["id"]
    foreign_order = client.get(f"/api/v1/custom-orders/{oid}", headers=owner_b)
    assert foreign_order.status_code == 404, foreign_order.get_json()


def test_gate_audit_and_api_envelopes(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "bakery_sweet")
    cat_id = _category(client, owner, "Gate-Audit")
    muffin = _item(client, owner, cat_id, "Gate Muffin", stock_quantity="1")
    mix = _item(client, owner, cat_id, "Gate Mix", stock_quantity="10")
    recipe = _recipe(client, owner, muffin["id"], [{"id": mix["id"], "qty": "1"}])

    produced = client.post(
        "/api/v1/productions",
        headers=owner,
        json={"recipe_id": recipe["id"], "quantity": "1"},
    )
    assert produced.get_json()["success"] is True

    order = client.post(
        "/api/v1/custom-orders",
        headers=owner,
        json={"title": "Audit Cake", "total_amount": "600", "advance_amount": "50"},
    )
    assert order.get_json()["success"] is True

    actions = _audit_actions(client, owner)
    assert "CREATE_PRODUCTION" in actions
    assert "CREATE_CUSTOM_ORDER" in actions
