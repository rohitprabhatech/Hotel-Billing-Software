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


def test_login_create_bill_and_password_change_are_audited(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    login_rows = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "LOGIN"},
    ).get_json()["data"]
    assert any(r["action"] == "LOGIN" for r in login_rows)

    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Auth Audit Cat"},
    ).get_json()["data"]["id"]
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Auth Audit Item",
            "category_id": category_id,
            "price": 90,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item_id, "quantity": 1}]},
    ).get_json()["data"]

    create_rows = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "CREATE_BILL"},
    ).get_json()["data"]
    assert any(
        r["action"] == "CREATE_BILL" and r.get("bill_number") == bill["bill_number"]
        for r in create_rows
    )

    changed = client.post(
        "/api/v1/auth/change-password",
        headers=billing,
        json={
            "current_password": "Billing@12345",
            "new_password": "Billing@99999",
            "confirm_password": "Billing@99999",
        },
    )
    assert changed.status_code == 200, changed.get_json()

    password_rows = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "PASSWORD_CHANGED"},
    ).get_json()["data"]
    assert any(r["action"] == "PASSWORD_CHANGED" for r in password_rows)

    # Restore demo password for other tests in this process
    restored = client.post(
        "/api/v1/auth/change-password",
        headers=login(client, "billing@hotela.com", "Billing@99999"),
        json={
            "current_password": "Billing@99999",
            "new_password": "Billing@12345",
            "confirm_password": "Billing@12345",
        },
    )
    assert restored.status_code == 200, restored.get_json()


def test_item_activity_survives_deactivate(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Survive Cat"},
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "Survive Item",
            "category_id": category_id,
            "price": 40,
            "gst_percentage": 5,
        },
    ).get_json()["data"]

    client.patch(
        f"/api/v1/items/{item['id']}/status",
        headers=billing,
        json={"is_active": False, "reason": "Out of stock"},
    )

    rows = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"entity_type": "ITEM", "entity_id": item["id"]},
    ).get_json()["data"]
    actions = {r["action"] for r in rows}
    assert "ITEM_CREATED" in actions
    assert "ITEM_DEACTIVATED" in actions

    deactivated = next(r for r in rows if r["action"] == "ITEM_DEACTIVATED")
    detail = client.get(f"/api/v1/audit-logs/{deactivated['id']}", headers=owner).get_json()[
        "data"
    ]
    assert detail["new_data"]["name"] == "Survive Item"
    assert detail["new_data"].get("reason") == "Out of stock"


def test_audit_forbidden_message_is_generic(client):
    _, billing, _ = _create_bill_with_cancel(client)
    response = client.get("/api/v1/audit-logs", headers=billing)
    assert response.status_code == 403
    assert "hotel" not in response.get_json()["error"]["message"].lower()
