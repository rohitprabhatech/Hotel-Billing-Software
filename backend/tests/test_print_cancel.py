"""Print, cancel, and bill history tests."""

from app.extensions import db
from app.models.audit_log import AuditLog
from tests.conftest import login


def _menu_and_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Print Cat"},
    ).get_json()["data"]["id"]
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Print Item",
            "category_id": category_id,
            "price": 100,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item_id, "quantity": 1}]},
    ).get_json()["data"]
    return owner, billing, bill


def test_cancel_requires_reason_and_keeps_record(client):
    owner, billing, bill = _menu_and_bill(client)

    bad = client.post(f"/api/v1/bills/{bill['id']}/cancel", headers=billing, json={})
    assert bad.status_code == 400

    ok = client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=billing,
        json={"reason": "Customer cancelled order"},
    )
    assert ok.status_code == 200
    data = ok.get_json()["data"]
    assert data["status"] == "CANCELLED"
    assert data["cancellation_reason"] == "Customer cancelled order"
    assert data["items"]

    # Still readable
    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert detail["status"] == "CANCELLED"

    actions = {
        row.action
        for row in db.session.query(AuditLog).filter(AuditLog.entity_id == bill["id"]).all()
    }
    assert "CANCEL_BILL" in actions


def test_print_and_reprint_audit(client):
    _, billing, bill = _menu_and_bill(client)

    first = client.post(f"/api/v1/bills/{bill['id']}/print", headers=billing)
    assert first.status_code == 200
    assert first.get_json()["data"]["action"] == "PRINT_BILL"
    assert first.get_json()["data"]["printed_count"] == 1

    second = client.post(f"/api/v1/bills/{bill['id']}/print", headers=billing)
    assert second.status_code == 200
    assert second.get_json()["data"]["action"] == "REPRINT_BILL"
    assert second.get_json()["data"]["printed_count"] == 2

    actions = {
        row.action
        for row in db.session.query(AuditLog).filter(AuditLog.entity_id == bill["id"]).all()
    }
    assert "PRINT_BILL" in actions
    assert "REPRINT_BILL" in actions


def test_bill_search_by_number(client):
    owner, _, bill = _menu_and_bill(client)
    res = client.get(f"/api/v1/bills?q={bill['bill_number']}", headers=owner)
    assert res.status_code == 200
    rows = res.get_json()["data"]
    assert len(rows) == 1
    assert rows[0]["id"] == bill["id"]


def test_cannot_cancel_twice(client):
    _, billing, bill = _menu_and_bill(client)
    client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=billing,
        json={"reason": "First cancel"},
    )
    again = client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=billing,
        json={"reason": "Second cancel"},
    )
    assert again.status_code == 400


def test_bill_detail_includes_business_for_print(client):
    owner, billing, bill = _menu_and_bill(client)
    detail = client.get(f"/api/v1/bills/{bill['id']}", headers=billing).get_json()["data"]
    assert detail["bill_number"] == bill["bill_number"]
    assert detail["tenant"]["business_name"]
    assert "business_type" in detail["tenant"]
    assert detail["items"]
    assert "unit_price" in detail["items"][0]

    # Cancelled bills remain printable with cancelled status
    client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=billing,
        json={"reason": "Wrong order"},
    )
    cancelled = client.get(f"/api/v1/bills/{bill['id']}", headers=owner).get_json()["data"]
    assert cancelled["status"] == "CANCELLED"
    assert cancelled["tenant"]["business_name"]
    assert cancelled["items"][0]["item_name"] == "Print Item"


def test_bill_search_by_reference(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Ref Cat"},
    ).get_json()["data"]["id"]
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Ref Item",
            "category_id": category_id,
            "price": 50,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "reference": "TOKEN-77",
            "items": [{"item_id": item_id, "quantity": 1}],
        },
    ).get_json()["data"]
    assert bill["reference"] == "TOKEN-77"

    res = client.get("/api/v1/bills", headers=owner, query_string={"q": "TOKEN-77"})
    assert res.status_code == 200
    rows = res.get_json()["data"]
    assert any(row["id"] == bill["id"] for row in rows)
