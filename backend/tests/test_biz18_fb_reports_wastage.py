"""Sprint BIZ-18 — F&B reports and food wastage."""

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


def test_restaurant_tenant_has_wastage_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "wastage" in enabled


def test_cafe_tenant_has_wastage_module(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    enabled = response.get_json()["data"]["enabled_modules"]
    assert "wastage" in enabled


def test_fb_report_channel_breakdown(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "FB Report Cat")
    item = _item(client, headers, cat_id, "FB Dish", is_menu=True)

    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]

    client.post(
        f"/api/v1/orders/{order['id']}/settle",
        headers=headers,
        json={"payment_method": "cash"},
    )

    report = client.get("/api/v1/reports/fb", headers=headers)
    assert report.status_code == 200, report.get_json()
    data = report.get_json()["data"]
    channels = {row["channel"]: row for row in data["channel_wise"]}
    assert "takeaway" in channels
    assert channels["takeaway"]["bill_count"] >= 1
    assert channels["takeaway"]["total_sales"] > 0


def test_wastage_deducts_stock_and_creates_movement(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Wastage Cat")
    ingredient = _item(client, headers, cat_id, "Tomato", stock="10")

    created = client.post(
        "/api/v1/wastage",
        headers=headers,
        json={"item_id": ingredient["id"], "quantity": "2.5", "reason": "Spoiled"},
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["quantity"] == 2.5
    assert body["stock_movement_id"]

    item_state = client.get(f"/api/v1/items/{ingredient['id']}", headers=headers).get_json()["data"]
    assert item_state["stock_quantity"] == 7.5

    movements = client.get(
        "/api/v1/stock-movements",
        headers=headers,
        query_string={"item_id": ingredient["id"], "source": "WASTAGE", "per_page": 5},
    ).get_json()["data"]
    assert len(movements) >= 1
    assert movements[0]["source"] == "WASTAGE"


def test_wastage_blocks_insufficient_stock(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "Low Stock Cat")
    ingredient = _item(client, headers, cat_id, "Mint", stock="0.5")

    response = client.post(
        "/api/v1/wastage",
        headers=headers,
        json={"item_id": ingredient["id"], "quantity": "1"},
    )
    assert response.status_code == 400, response.get_json()


def test_clothing_tenant_cannot_access_wastage(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    client.put("/api/v1/tenants/me", headers=headers, json={"business_type": "clothing"})
    response = client.get("/api/v1/wastage", headers=headers)
    assert response.status_code == 403, response.get_json()
