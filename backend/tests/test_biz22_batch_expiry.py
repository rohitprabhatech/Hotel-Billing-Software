"""Sprint BIZ-22 — grocery batch expiry and stock adjustment reasons."""

from datetime import date, timedelta

from tests.conftest import login


def _switch_grocery(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "grocery_kirana"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Expiry Cat"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "50",
        "gst_percentage": "0",
        "stock_quantity": "0",
        "uom": "pcs",
        "tracks_batches": True,
        "block_expired_batches": True,
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_grocery_has_batch_expiry_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    modules = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert "batch_expiry" in modules.get_json()["data"]["enabled_modules"]


def test_batches_forbidden_for_restaurant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    denied = client.get("/api/v1/batches/expiry", headers=headers)
    assert denied.status_code == 403, denied.get_json()


def test_adjust_stock_requires_reason_on_grocery(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    item = _item(
        client,
        headers,
        cat_id,
        "Plain Stock",
        tracks_batches=False,
        stock_quantity="10",
    )
    missing = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=headers,
        json={"delta": "-1"},
    )
    assert missing.status_code == 400, missing.get_json()

    ok = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=headers,
        json={"delta": "-1", "reason": "Damaged packet"},
    )
    assert ok.status_code == 200, ok.get_json()
    assert float(ok.get_json()["data"]["stock_quantity"]) == 9.0


def test_receive_batch_and_expiry_report(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    milk = _item(client, headers, cat_id, "Milk Pouch", stock_quantity="0")

    soon = (date.today() + timedelta(days=3)).isoformat()
    later = (date.today() + timedelta(days=30)).isoformat()
    past = (date.today() - timedelta(days=1)).isoformat()

    b1 = client.post(
        "/api/v1/batches",
        headers=headers,
        json={
            "item_id": milk["id"],
            "quantity": "5",
            "expiry_date": soon,
            "batch_code": "M-SOON",
        },
    )
    assert b1.status_code == 201, b1.get_json()

    b2 = client.post(
        "/api/v1/batches",
        headers=headers,
        json={
            "item_id": milk["id"],
            "quantity": "8",
            "expiry_date": later,
            "batch_code": "M-LATER",
        },
    )
    assert b2.status_code == 201, b2.get_json()

    expired_batch = client.post(
        "/api/v1/batches",
        headers=headers,
        json={
            "item_id": milk["id"],
            "quantity": "4",
            "expiry_date": past,
            "batch_code": "M-OLD",
        },
    )
    assert expired_batch.status_code == 201, expired_batch.get_json()

    item = client.get(f"/api/v1/items/{milk['id']}", headers=headers).get_json()["data"]
    assert float(item["stock_quantity"]) == 17.0

    report = client.get("/api/v1/batches/expiry", headers=headers, query_string={"within_days": 7})
    assert report.status_code == 200, report.get_json()
    body = report.get_json()["data"]
    assert body["summary"]["expired_count"] >= 1
    assert body["summary"]["expiring_count"] >= 1
    assert any(row["batch_code"] == "M-SOON" for row in body["expiring"])
    assert any(row["batch_code"] == "M-OLD" for row in body["expired"])

    alias = client.get("/api/v1/grocery/expiry", headers=headers)
    assert alias.status_code == 200, alias.get_json()


def test_expired_batch_not_sellable_when_policy_on(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    yogurt = _item(client, headers, cat_id, "Yogurt Cup", stock_quantity="0")
    past = (date.today() - timedelta(days=2)).isoformat()
    future = (date.today() + timedelta(days=20)).isoformat()

    client.post(
        "/api/v1/batches",
        headers=headers,
        json={
            "item_id": yogurt["id"],
            "quantity": "10",
            "expiry_date": past,
            "batch_code": "Y-EXP",
        },
    )
    client.post(
        "/api/v1/batches",
        headers=headers,
        json={
            "item_id": yogurt["id"],
            "quantity": "3",
            "expiry_date": future,
            "batch_code": "Y-OK",
        },
    )

    # Total stock 13 but sellable 3
    blocked = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": yogurt["id"], "quantity": "5"}],
        },
    )
    assert blocked.status_code == 400, blocked.get_json()
    assert blocked.get_json()["error"]["code"] == "INSUFFICIENT_STOCK"

    ok = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": yogurt["id"], "quantity": "2"}],
        },
    )
    assert ok.status_code == 201, ok.get_json()

    batches = client.get(
        "/api/v1/batches",
        headers=headers,
        query_string={"item_id": yogurt["id"]},
    )
    assert batches.status_code == 200
    rows = {row["batch_code"]: row for row in batches.get_json()["data"]}
    assert float(rows["Y-OK"]["quantity"]) == 1.0
    assert float(rows["Y-EXP"]["quantity"]) == 10.0


def test_batch_adjust_requires_reason(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    item = _item(client, headers, cat_id, "Bread Loaf")
    created = client.post(
        "/api/v1/batches",
        headers=headers,
        json={
            "item_id": item["id"],
            "quantity": "6",
            "expiry_date": (date.today() + timedelta(days=5)).isoformat(),
            "batch_code": "B1",
        },
    )
    batch_id = created.get_json()["data"]["id"]

    missing = client.post(
        f"/api/v1/batches/{batch_id}/adjust",
        headers=headers,
        json={"delta": "-1"},
    )
    assert missing.status_code == 400, missing.get_json()

    ok = client.post(
        f"/api/v1/batches/{batch_id}/adjust",
        headers=headers,
        json={"delta": "-1", "reason": "Broken packaging"},
    )
    assert ok.status_code == 200, ok.get_json()
    assert float(ok.get_json()["data"]["quantity"]) == 5.0


def test_receive_stock_blocked_when_tracks_batches(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_grocery(client, headers)
    cat_id = _category(client, headers)
    item = _item(client, headers, cat_id, "Cheese Block")
    denied = client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=headers,
        json={"quantity": "5", "reason": "Delivery"},
    )
    assert denied.status_code == 400, denied.get_json()
