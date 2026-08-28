"""CLTH-6 — clothing billing polish gate (frontend sprint sign-off).

Extends BIZ-28 with period-based sales (owner dashboard), customer on bills,
and hotel/cafe regression after clothing tenant switch.

Run from backend/ with FLASK_ENV=testing:
  python -m pytest tests/test_biz25_clothing_variants.py tests/test_biz26_clothing_images_pos.py
    tests/test_biz27_clothing_returns.py tests/test_biz28_clothing_reports_and_testing_gate.py
    tests/test_clth_billing_polish_gate.py -q

Hotel/cafe regression (unchanged tenants):
  python -m pytest tests/test_biz19_restaurant_cafe_testing_gate.py tests/test_cafe_stock_sprint6.py -q
"""

from tests.conftest import login
from tests.test_biz28_clothing_reports_and_testing_gate import (
    _category,
    _customer,
    _item,
    _sell,
    _switch_clothing,
    _variant,
)


def _switch_hotel(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "hotel_restaurant"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def test_clothing_sales_accepts_period_param(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers, "CLTH6 Period")
    item = _item(client, headers, cat_id, "Period Tee")
    variant = _variant(
        client,
        headers,
        item["id"],
        size="M",
        color="Grey",
        brand="PeriodBrand",
        stock_quantity="5",
    )
    _sell(client, headers, item["id"], variant["id"], "1")

    report = client.get(
        "/api/v1/clothing/sales",
        headers=headers,
        query_string={"period": "last_7_days"},
    )
    assert report.status_code == 200, report.get_json()
    data = report.get_json()["data"]
    assert data["period"] == "last_7_days"
    assert data["metrics"]["bill_count"] >= 1
    assert any(row["size"] == "M" for row in data["by_size"])


def test_clothing_bill_with_customer_id(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers, "CLTH6 Customer")
    item = _item(client, headers, cat_id, "Customer Tee")
    variant = _variant(
        client,
        headers,
        item["id"],
        size="L",
        color="Blue",
        brand="WalkIn",
        stock_quantity="3",
    )
    customer = _customer(client, headers, "POS Shopper", "9876500101")
    bill = _sell(client, headers, item["id"], variant["id"], "1", customer_id=customer["id"])

    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=headers)
    assert detail.status_code == 200, detail.get_json()
    assert detail.get_json()["data"]["customer_id"] == customer["id"]


def test_hotel_regression_after_clothing_switch_back(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    assert client.get("/api/v1/clothing/pos-catalog", headers=headers).status_code == 200

    _switch_hotel(client, headers)
    assert client.get("/api/v1/clothing/pos-catalog", headers=headers).status_code == 403

    table = client.post(
        "/api/v1/tables",
        headers=headers,
        json={"code": "CLTH6-R1", "capacity": 4},
    )
    assert table.status_code == 201, table.get_json()
    listing = client.get("/api/v1/tables", headers=headers)
    assert listing.status_code == 200, listing.get_json()
    codes = {row["code"] for row in listing.get_json()["data"]}
    assert "CLTH6-R1" in codes


def test_cafe_regression_clothing_endpoints_forbidden(client):
    cafe = login(client, "owner@hotelb.com", "Owner@12345")
    assert client.get("/api/v1/clothing/pos-catalog", headers=cafe).status_code == 403
    assert client.get("/api/v1/clothing/sales", headers=cafe).status_code == 403
    catalog = client.get("/api/v1/cafe/pos-catalog", headers=cafe)
    assert catalog.status_code == 200, catalog.get_json()
    assert catalog.get_json()["success"] is True


def test_barcode_lookup_works_for_clothing_variant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers, "CLTH6 Scan")
    item = _item(client, headers, cat_id, "Scan Tee")
    _variant(
        client,
        headers,
        item["id"],
        size="S",
        color="White",
        brand="ScanCo",
        barcode="8901001001999",
        stock_quantity="2",
    )

    lookup = client.get("/api/v1/items/by-barcode/8901001001999", headers=headers)
    assert lookup.status_code == 200, lookup.get_json()
    body = lookup.get_json()["data"]
    assert body["id"] == item["id"]
    assert body["matched_variant"]["size"] == "S"
    assert body["matched_variant"]["color"] == "White"
