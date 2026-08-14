"""P2-11: Owner sees Billing User LOGIN / CREATE_BILL / item activity; history survives deactivate."""

from tests.conftest import login


def test_owner_sees_billing_user_login_bill_and_item_lifecycle(client):
    """
    Acceptance: LOGIN, CREATE_BILL, and item create/edit/deactivate are visible
    to Owner after Billing User actions; item history survives soft-deactivate.
    """
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    users = client.get("/api/v1/users", headers=owner).get_json()["data"]
    billing_user = next(u for u in users if u["role"] == "BILLING_USER")
    billing_id = billing_user["id"]

    # --- LOGIN (billing session) ---
    login_rows = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "LOGIN", "user_id": billing_id},
    ).get_json()["data"]
    assert any(r["action"] == "LOGIN" and r["user_id"] == billing_id for r in login_rows)

    # --- Catalog setup (owner creates category; billing owns item lifecycle) ---
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "P2-11 Grocery"},
    ).get_json()["data"]["id"]

    item = client.post(
        "/api/v1/items",
        headers=billing,
        json={
            "name": "P2-11 Dal 1kg",
            "category_id": category_id,
            "price": 140,
            "gst_percentage": 5,
        },
    ).get_json()["data"]
    item_id = item["id"]

    updated = client.put(
        f"/api/v1/items/{item_id}",
        headers=billing,
        json={"price": 155, "name": "P2-11 Dal 1kg Premium"},
    )
    assert updated.status_code == 200

    # --- CREATE_BILL by billing ---
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item_id, "quantity": 1}],
        },
    ).get_json()["data"]

    create_bill_rows = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "CREATE_BILL", "user_id": billing_id},
    ).get_json()["data"]
    assert any(
        r["action"] == "CREATE_BILL"
        and r["user_id"] == billing_id
        and r.get("bill_number") == bill["bill_number"]
        for r in create_bill_rows
    )

    # Soft-deactivate (billing) — catalog hide, history must remain
    deactivated = client.patch(
        f"/api/v1/items/{item_id}/status",
        headers=billing,
        json={"is_active": False, "reason": "P2-11 out of stock"},
    )
    assert deactivated.status_code == 200
    assert deactivated.get_json()["data"]["is_active"] is False

    # Owner Item Activity path: entity_type=ITEM (same as ItemActivityPage)
    activity = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"entity_type": "ITEM", "entity_id": item_id},
    ).get_json()["data"]
    actions = {r["action"] for r in activity}
    assert "ITEM_CREATED" in actions
    assert "ITEM_UPDATED" in actions
    assert "ITEM_DEACTIVATED" in actions
    assert all(r["entity_id"] == item_id for r in activity)
    assert any(r["user_id"] == billing_id for r in activity)

    deactivate_row = next(r for r in activity if r["action"] == "ITEM_DEACTIVATED")
    detail = client.get(
        f"/api/v1/audit-logs/{deactivate_row['id']}",
        headers=owner,
    ).get_json()["data"]
    assert detail["new_data"].get("reason") == "P2-11 out of stock"
    # Snapshot retained after deactivate (not wiped with catalog soft-delete)
    assert "Dal" in (detail["new_data"].get("name") or "")

    # Billing user still cannot read audit / item activity
    assert client.get("/api/v1/audit-logs", headers=billing).status_code == 403
