"""Sprint BIZ-32 — mobile brand/model catalog and purchase history."""

from tests.conftest import login


def _switch_mobile(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "mobile"},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Mobile"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "15000",
        "gst_percentage": "18",
        "tracks_serial": True,
        "stock_quantity": "0",
        "uom": "pcs",
        "brand": "Samsung",
        "model_name": "Galaxy A15",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_item_brand_model_fields(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner)
    phone = _item(client, owner, cat_id, "Galaxy Phone")
    assert phone["brand"] == "Samsung"
    assert phone["model_name"] == "Galaxy A15"

    updated = client.put(
        f"/api/v1/items/{phone['id']}",
        headers=owner,
        json={"brand": "Apple", "model_name": "iPhone 15"},
    )
    assert updated.status_code == 200, updated.get_json()
    body = updated.get_json()["data"]
    assert body["brand"] == "Apple"
    assert body["model_name"] == "iPhone 15"


def test_mobile_sales_by_brand_and_model(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner)
    phone = _item(client, owner, cat_id, "Report Phone", brand="Xiaomi", model_name="Redmi 13")
    client.post(
        "/api/v1/serial-units",
        headers=owner,
        json={"item_id": phone["id"], "serial": "SNMOBILE3201"},
    )
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": phone["id"], "serial": "SNMOBILE3201", "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()

    report = client.get("/api/v1/mobile/sales", headers=owner)
    assert report.status_code == 200, report.get_json()
    data = report.get_json()["data"]
    brands = {row["brand"]: row for row in data["by_brand"]}
    assert "Xiaomi" in brands
    assert brands["Xiaomi"]["bill_count"] >= 1
    models = {row["model_name"]: row for row in data["by_model"]}
    assert "Redmi 13" in models
    assert data["serial_stock_summary"]["SOLD"] >= 1


def test_mobile_customer_history_shows_imei(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner, "Phones")
    phone = _item(client, owner, cat_id, "History Phone", brand="Vivo", model_name="Y27")
    client.post(
        "/api/v1/serial-units",
        headers=owner,
        json={"item_id": phone["id"], "serial": "SNHIST3202"},
    )
    customer = client.post(
        "/api/v1/customers",
        headers=owner,
        json={"name": "Ramesh", "phone_country_code": "91", "phone": "9123456780"},
    )
    assert customer.status_code == 201, customer.get_json()
    customer_id = customer.get_json()["data"]["id"]

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "customer_id": customer_id,
            "items": [{"item_id": phone["id"], "serial": "SNHIST3202", "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()

    history = client.get(
        "/api/v1/mobile/customer-history",
        headers=owner,
        query_string={"customer_id": customer_id},
    )
    assert history.status_code == 200, history.get_json()
    bills = history.get_json()["data"]["bills"]
    assert len(bills) >= 1
    assert bills[0]["items"][0]["serial_number"] == "SNHIST3202"


def test_restaurant_mobile_reports_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    denied = client.get("/api/v1/mobile/sales", headers=headers)
    assert denied.status_code == 403
