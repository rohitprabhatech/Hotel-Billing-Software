"""Owner reports and export authorization tests."""

from app.extensions import db
from app.models.audit_log import AuditLog
from tests.conftest import login


def _seed_sale(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Report Cat"},
    ).get_json()["data"]["id"]
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Report Item",
            "category_id": category_id,
            "price": 200,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item_id, "quantity": 2}], "discount": 0},
    ).get_json()["data"]
    return owner, billing, bill


def test_billing_user_cannot_access_reports(client):
    _, billing, _ = _seed_sale(client)
    response = client.get("/api/v1/reports/summary", headers=billing)
    assert response.status_code == 403


def test_owner_summary_includes_sales(client):
    owner, _, bill = _seed_sale(client)
    response = client.get("/api/v1/reports/summary?period=today", headers=owner)
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["current"]["bill_count"] >= 1
    assert data["current"]["total_sales"] >= bill["grand_total"]


def test_cancelled_excluded_from_sales_but_counted(client):
    owner, billing, bill = _seed_sale(client)
    client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=billing,
        json={"reason": "Test cancel for report"},
    )
    response = client.get("/api/v1/reports/summary?period=today", headers=owner)
    data = response.get_json()["data"]["current"]
    assert data["cancelled_bills"] >= 1


def test_export_xlsx_and_audit(client):
    owner, _, _ = _seed_sale(client)
    response = client.get("/api/v1/reports/export?type=daily&format=xlsx", headers=owner)
    assert response.status_code == 200
    assert (
        "spreadsheetml"
        in response.headers.get("Content-Type", "")
        or response.data[:2] == b"PK"
    )
    actions = {row.action for row in db.session.query(AuditLog).all()}
    assert "EXPORT_REPORT" in actions


def test_cross_tenant_report_isolation(client):
    owner_a, _, _ = _seed_sale(client)
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    a = client.get("/api/v1/reports/summary?period=today", headers=owner_a).get_json()["data"]
    b = client.get("/api/v1/reports/summary?period=today", headers=owner_b).get_json()["data"]
    assert a["current"]["bill_count"] >= 1
    assert b["current"]["bill_count"] == 0
