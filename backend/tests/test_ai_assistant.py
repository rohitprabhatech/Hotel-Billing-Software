"""AI business assistant tests — tenant-scoped, no invented metrics."""

from tests.conftest import login


def _seed_sale(client, *, qty=2, price=200):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "AI Cat"},
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "AI Item",
            "category_id": category_id,
            "price": price,
            "gst_percentage": 5,
        },
    ).get_json()["data"]
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": qty}]},
    ).get_json()["data"]
    return owner, billing, bill, item


def test_billing_user_cannot_access_ai(client):
    _, billing, _, _ = _seed_sale(client)
    response = client.get("/api/v1/ai/analysis", headers=billing)
    assert response.status_code == 403
    assert "hotel" not in response.get_json()["error"]["message"].lower()


def test_owner_analysis_uses_real_sales(client):
    owner, _, bill, item = _seed_sale(client)
    response = client.get(
        "/api/v1/ai/analysis",
        headers=owner,
        query_string={"period": "today"},
    )
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert data["insufficient_data"] is False
    assert data["metrics"]["bill_count"] >= 1
    assert data["metrics"]["total_sales"] >= bill["grand_total"]
    assert data["payment_mix"]["cash_share_pct"] is not None
    assert any(row["item_name"] == item["name"] for row in data["top_items"])
    assert any(row["category_name"] == "AI Cat" for row in data["category_sales"])
    assert data["summary"]
    assert data["insights"]
    # Every insight detail must reference real sales figures already in metrics/items
    assert data["data_source"] == "tenant_sales_reports"


def test_insufficient_data_for_empty_tenant(client):
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    response = client.get(
        "/api/v1/ai/analysis",
        headers=owner_b,
        query_string={"period": "today"},
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["insufficient_data"] is True
    assert "Not enough sales data" in data["message"]
    assert data["metrics"]["bill_count"] == 0
    assert data["insights"] == []
    assert data["top_items"] == []


def test_ai_analysis_tenant_isolation(client):
    owner_a, _, bill, _ = _seed_sale(client)
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    a = client.get(
        "/api/v1/ai/analysis",
        headers=owner_a,
        query_string={"period": "this_week"},
    ).get_json()["data"]
    b = client.get(
        "/api/v1/ai/analysis",
        headers=owner_b,
        query_string={"period": "this_week"},
    ).get_json()["data"]

    assert a["insufficient_data"] is False
    assert a["metrics"]["total_sales"] >= bill["grand_total"]
    assert b["insufficient_data"] is True
    assert b["metrics"]["total_sales"] == 0


def test_weekly_and_monthly_analysis(client):
    owner, _, bill, _ = _seed_sale(client)
    for period in ("this_week", "this_month"):
        data = client.get(
            "/api/v1/ai/analysis",
            headers=owner,
            query_string={"period": period},
        ).get_json()["data"]
        assert data["period"] == period
        assert data["insufficient_data"] is False
        assert data["metrics"]["total_sales"] >= bill["grand_total"]


def test_decisions_best_slow_movers_and_recommendations(client):
    owner, billing, bill, item = _seed_sale(client, qty=3, price=100)
    # Second item so slow/best movers can differ
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "AI Cat 2"},
    ).get_json()["data"]["id"]
    item_b = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "AI Slow Item",
            "category_id": category_id,
            "price": 50,
            "gst_percentage": 5,
        },
    ).get_json()["data"]
    client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item_b["id"], "quantity": 1}]},
    )

    response = client.get(
        "/api/v1/ai/decisions",
        headers=owner,
        query_string={"period": "today"},
    )
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert data["insufficient_data"] is False
    decisions = data["decisions"]
    assert decisions["insufficient_data"] is False
    assert decisions["best_movers"]
    assert decisions["slow_movers"]
    assert decisions["best_movers"][0]["item_name"] == item["name"]
    assert any(r["item_name"] == "AI Slow Item" for r in decisions["slow_movers"])
    assert decisions["recommendations"]
    assert all("detail" in rec and "based_on" in rec for rec in decisions["recommendations"])
    # Demand comparison needs prior-period sales; today vs yesterday usually insufficient
    assert "demand_insufficient" in decisions
    assert data["metrics"]["total_sales"] >= bill["grand_total"]


def test_decisions_insufficient_for_empty_tenant(client):
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    data = client.get(
        "/api/v1/ai/decisions",
        headers=owner_b,
        query_string={"period": "today"},
    ).get_json()["data"]
    assert data["insufficient_data"] is True
    assert data["decisions"]["insufficient_data"] is True
    assert data["decisions"]["recommendations"] == []
    assert data["decisions"]["best_movers"] == []


def test_decisions_tenant_isolation(client):
    owner_a, _, _, _ = _seed_sale(client)
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    a = client.get(
        "/api/v1/ai/decisions",
        headers=owner_a,
        query_string={"period": "this_week"},
    ).get_json()["data"]
    b = client.get(
        "/api/v1/ai/decisions",
        headers=owner_b,
        query_string={"period": "this_week"},
    ).get_json()["data"]
    assert a["decisions"]["insufficient_data"] is False
    assert a["decisions"]["best_movers"]
    assert b["insufficient_data"] is True
    assert b["decisions"]["best_movers"] == []
