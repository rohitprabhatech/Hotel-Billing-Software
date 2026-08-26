"""Sprint BIZ-62 — rule-based industry AI analyzers."""

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def test_restaurant_gets_fb_industry_insights_only(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hotel_restaurant")

    cat = client.post(
        "/api/v1/categories", headers=owner, json={"name": "AI FB Cat"}
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={"name": "AI Thali", "category_id": cat, "price": 150, "gst_percentage": 0},
    ).get_json()["data"]["id"]
    assert (
        client.post(
            "/api/v1/bills",
            headers=billing,
            json={"items": [{"item_id": item, "quantity": 1}]},
        ).status_code
        == 201
    )

    data = client.get(
        "/api/v1/ai/analysis",
        headers=owner,
        query_string={"period": "today"},
    ).get_json()["data"]
    assert data["analysis_mode"] == "rule_based"
    modules = {block["module"] for block in data["industry_insights"]}
    assert "order_channels" in modules
    assert "serial_imei" not in modules
    assert "travel_commission" not in modules


def test_clothing_does_not_get_fb_insights(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "clothing")
    data = client.get(
        "/api/v1/ai/analysis",
        headers=owner,
        query_string={"period": "today"},
    ).get_json()["data"]
    modules = {block["module"] for block in data.get("industry_insights") or []}
    assert "order_channels" not in modules
    assert "serial_imei" not in modules
    # clothing has neither customer_credit nor serial in defaults for clothing?
    # clothing: variants, product_images, returns_exchange, barcode_pos — no credit
    assert "customer_credit" not in modules


def test_travel_gets_commission_analyzer(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    data = client.get(
        "/api/v1/ai/analysis",
        headers=owner,
        query_string={"period": "today"},
    ).get_json()["data"]
    modules = {block["module"] for block in data["industry_insights"]}
    assert "travel_commission" in modules
    assert "order_channels" not in modules
    assert "serial_imei" not in modules


def test_industry_insights_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "grocery_kirana")
    _switch(client, owner_b, "grocery_kirana")

    # Seed credit on A only
    customer = client.post(
        "/api/v1/customers",
        headers=owner_a,
        json={"name": "AI Credit", "phone_country_code": "91", "phone": "9000000062"},
    ).get_json()["data"]
    cat = client.post(
        "/api/v1/categories", headers=owner_a, json={"name": "AI Groc"}
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner_a,
        json={"name": "AI Rice", "category_id": cat, "price": 50, "gst_percentage": 0},
    ).get_json()["data"]["id"]
    billing = login(client, "billing@hotela.com", "Billing@12345")
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "customer_id": customer["id"],
            "items": [{"item_id": item, "quantity": 2}],
            "payment_method": "credit",
        },
    )
    assert bill.status_code == 201, bill.get_json()

    a = client.get(
        "/api/v1/ai/analysis",
        headers=owner_a,
        query_string={"period": "today"},
    ).get_json()["data"]
    b = client.get(
        "/api/v1/ai/analysis",
        headers=owner_b,
        query_string={"period": "today"},
    ).get_json()["data"]

    credit_a = next(block for block in a["industry_insights"] if block["module"] == "customer_credit")
    credit_b = next(block for block in b["industry_insights"] if block["module"] == "customer_credit")
    assert credit_a["insufficient_data"] is False
    assert any(i["type"] == "credit_customer_outstanding" for i in credit_a["insights"])
    assert credit_b["insufficient_data"] is True or float(
        (credit_b.get("metrics") or {}).get("outstanding_amount") or 0
    ) == 0
