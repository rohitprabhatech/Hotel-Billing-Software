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
    assert bill["table_number"] == "41"
    assert bill["reference"] == "41"


def test_bill_reference_alias(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _create_menu(client, owner)

    via_reference = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "reference": "C-12",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    )
    assert via_reference.status_code == 201, via_reference.get_json()
    ref_bill = via_reference.get_json()["data"]
    assert ref_bill["reference"] == "C-12"
    assert ref_bill["table_number"] == "C-12"

    via_legacy = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "table_number": "T-9",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    assert via_legacy["reference"] == "T-9"
    assert via_legacy["table_number"] == "T-9"

    # reference wins when both are sent
    both = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "reference": "TOKEN-1",
            "table_number": "ignored",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    assert both["reference"] == "TOKEN-1"
    assert both["table_number"] == "TOKEN-1"


def test_payment_method_cash_and_online(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _create_menu(client, owner)

    # Omitted payment_method defaults to cash
    default_bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 1}]},
    ).get_json()["data"]
    assert default_bill["payment_method"] == "cash"
    assert default_bill["payment_method_label"] == "Cash"

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

    listed_online = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"payment_method": "online"},
    ).get_json()["data"]
    assert all(row["payment_method"] == "online" for row in listed_online)
    assert any(row["id"] == online_bill["id"] for row in listed_online)

    listed_cash = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"payment_method": "cash"},
    ).get_json()["data"]
    assert all(row["payment_method"] == "cash" for row in listed_cash)
    assert any(row["id"] == cash_bill["id"] for row in listed_cash)
    assert any(row["id"] == default_bill["id"] for row in listed_cash)

    bad_filter = client.get(
        "/api/v1/bills",
        headers=owner,
        query_string={"payment_method": "upi"},
    )
    assert bad_filter.status_code == 400

    report_online = client.get(
        "/api/v1/reports/daily-sales",
        headers=owner,
        query_string={"payment_method": "online"},
    ).get_json()["data"]
    assert report_online["metrics"]["online_sales"] >= online_bill["grand_total"]
    assert all(b["payment_method"] == "online" for b in report_online["bills"])
    assert "cash_bill_count" in report_online["metrics"]
    assert "online_bill_count" in report_online["metrics"]

    summary = client.get(
        "/api/v1/reports/summary",
        headers=owner,
        query_string={"period": "today"},
    ).get_json()["data"]
    assert "cash_bill_count" in summary["current"]
    assert "online_bill_count" in summary["current"]
    assert summary["current"]["cash_sales"] >= 0
    assert summary["current"]["online_sales"] >= 0


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
        json={"price": 500, "name": "Renamed Thali"},
    )

    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=billing).get_json()["data"]
    assert detail["items"][0]["unit_price"] == 420.0
    assert detail["items"][0]["item_name"] == "Chicken Sadhi Thali"
    assert detail["items"][0]["gst_percentage"] == 5.0
    assert detail["tenant"]["business_name"]

    current = db.session.get(Item, item["id"])
    assert float(current.price) == 500.0
    assert current.name == "Renamed Thali"


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
