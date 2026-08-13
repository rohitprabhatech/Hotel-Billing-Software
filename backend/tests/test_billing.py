"""Billing finalize API tests."""

from app.extensions import db
from app.models.item import Item
from tests.conftest import login


def _create_menu(client, headers):
    category_id = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": "Thali"},
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": "Chicken Sadhi Thali",
            "category_id": category_id,
            "price": 420,
            "gst_percentage": 5,
        },
    ).get_json()["data"]
    return item


def test_finalize_bill_server_totals(client):
    headers = login(client, "billing@hotela.com", "Billing@12345")
    # Owner creates menu
    owner = login(client, "owner@hotela.com", "Owner@12345")
    item = _create_menu(client, owner)

    response = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "table_number": "41",
            "discount": 20,
            "items": [{"item_id": item["id"], "quantity": 2}],
            "grand_total": 1,  # must be ignored / excluded by schema
        },
    )
    assert response.status_code == 201, response.get_json()
    bill = response.get_json()["data"]
    assert bill["status"] == "FINALIZED"
    assert bill["payment_method"] == "cash"
    assert bill["payment_method_label"] == "Cash"
    assert bill["subtotal"] == 840.0
    assert bill["discount"] == 20.0
    assert bill["taxable_amount"] == 820.0
    assert bill["cgst_amount"] == 20.5
    assert bill["sgst_amount"] == 20.5
    assert bill["grand_total"] == 861.0
    assert bill["items"][0]["item_name"] == "Chicken Sadhi Thali"
    assert bill["items"][0]["unit_price"] == 420.0
    assert bill["bill_number"]


def test_payment_method_cash_and_online(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _create_menu(client, owner)

    cash_bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    assert cash_bill["payment_method"] == "cash"

    online_bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "online",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    assert online_bill["payment_method"] == "online"
    assert online_bill["payment_method_label"] == "Online"

    invalid = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "upi",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    )
    assert invalid.status_code == 400

    listed = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"payment_method": "online"},
    ).get_json()["data"]
    assert all(row["payment_method"] == "online" for row in listed)
    assert any(row["id"] == online_bill["id"] for row in listed)

    report = client.get(
        "/api/v1/reports/daily-sales",
        headers=owner,
        query_string={"payment_method": "online"},
    ).get_json()["data"]
    assert report["metrics"]["online_sales"] >= online_bill["grand_total"]
    assert all(b["payment_method"] == "online" for b in report["bills"])


def test_historical_price_snapshot(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _create_menu(client, owner)

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 1}]},
    ).get_json()["data"]

    client.put(
        f"/api/v1/items/{item['id']}",
        headers=owner,
        json={"price": 500},
    )

    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=billing).get_json()["data"]
    assert detail["items"][0]["unit_price"] == 420.0

    current = db.session.get(Item, item["id"])
    assert float(current.price) == 500.0


def test_unique_bill_numbers(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _create_menu(client, owner)

    b1 = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 1}]},
    ).get_json()["data"]
    b2 = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 1}]},
    ).get_json()["data"]
    assert b1["bill_number"] != b2["bill_number"]
    assert b1["bill_sequence"] != b2["bill_sequence"]


def test_inactive_item_rejected(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _create_menu(client, owner)
    client.patch(
        f"/api/v1/items/{item['id']}/status",
        headers=owner,
        json={"is_active": False},
    )
    response = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 1}]},
    )
    assert response.status_code == 400


def test_cross_tenant_bill_access_denied(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    billing_a = login(client, "billing@hotela.com", "Billing@12345")
    item = _create_menu(client, owner_a)
    bill = client.post(
        "/api/v1/bills",
        headers=billing_a,
        json={"items": [{"item_id": item["id"], "quantity": 1}]},
    ).get_json()["data"]

    response = client.get(f"/api/v1/bills/{bill['id']}", headers=owner_b)
    assert response.status_code == 404
