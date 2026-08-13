"""Audit log API tests."""

from tests.conftest import login


def _create_bill_with_cancel(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Audit Cat"},
    ).get_json()["data"]["id"]
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Audit Item",
            "category_id": category_id,
            "price": 150,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item_id, "quantity": 1}]},
    ).get_json()["data"]
    client.post(
        f"/api/v1/bills/{bill['id']}/cancel",
        headers=billing,
        json={"reason": "Customer order cancelled"},
    )
    return owner, billing, bill


def test_billing_user_cannot_access_audit_logs(client):
    _, billing, _ = _create_bill_with_cancel(client)
    response = client.get("/api/v1/audit-logs", headers=billing)
    assert response.status_code == 403


def test_owner_can_list_and_filter_cancel(client):
    owner, _, bill = _create_bill_with_cancel(client)
    response = client.get("/api/v1/audit-logs?action=CANCEL_BILL", headers=owner)
    assert response.status_code == 200
    rows = response.get_json()["data"]
    assert any(r["action"] == "CANCEL_BILL" for r in rows)

    by_bill = client.get(
        f"/api/v1/audit-logs?bill_number={bill['bill_number']}",
        headers=owner,
    )
    assert by_bill.status_code == 200
    assert len(by_bill.get_json()["data"]) >= 1


def test_audit_detail_shows_cancel_reason(client):
    owner, _, _ = _create_bill_with_cancel(client)
    rows = client.get("/api/v1/audit-logs?action=CANCEL_BILL", headers=owner).get_json()[
        "data"
    ]
    detail = client.get(f"/api/v1/audit-logs/{rows[0]['id']}", headers=owner)
    assert detail.status_code == 200
    data = detail.get_json()["data"]
    assert data["new_data"]["cancellation_reason"] == "Customer order cancelled"
    assert data["new_data"]["grand_total"] is not None


def test_alerts_endpoint(client):
    owner, _, _ = _create_bill_with_cancel(client)
    response = client.get("/api/v1/audit-logs/alerts", headers=owner)
    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert "alerts" in payload
    assert any(a["type"] == "LOGIN_ACTIVITY" for a in payload["alerts"])


def test_no_delete_audit_endpoint(client):
    owner, _, _ = _create_bill_with_cancel(client)
    rows = client.get("/api/v1/audit-logs", headers=owner).get_json()["data"]
    response = client.delete(f"/api/v1/audit-logs/{rows[0]['id']}", headers=owner)
    assert response.status_code in {404, 405}


def test_cross_tenant_audit_isolation(client):
    owner_a, _, _ = _create_bill_with_cancel(client)
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    a_logs = client.get("/api/v1/audit-logs", headers=owner_a).get_json()["data"]
    b_logs = client.get("/api/v1/audit-logs", headers=owner_b).get_json()["data"]
    assert any(r["action"] == "CANCEL_BILL" for r in a_logs)
    assert not any(r["action"] == "CANCEL_BILL" for r in b_logs)
