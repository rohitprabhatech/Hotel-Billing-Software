"""P2-13: Business A ↛ Business B isolation matrix (categories/items/bills/reports/users/audit/activity)."""

from tests.conftest import login


def _seed_bill(client, owner_headers, *, cat_name: str, item_name: str):
    category_id = client.post(
        "/api/v1/categories",
        headers=owner_headers,
        json={"name": cat_name},
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner_headers,
        json={
            "name": item_name,
            "category_id": category_id,
            "price": 100,
            "gst_percentage": 5,
        },
    ).get_json()["data"]
    bill = client.post(
        "/api/v1/bills",
        headers=owner_headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    return category_id, item, bill


def test_business_a_cannot_access_business_b_resources(client):
    """Isolation matrix: cross-tenant GET/list/mutate must not leak Business B into A (and reverse)."""
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    cat_a, item_a, bill_a = _seed_bill(
        client, owner_a, cat_name="P213-A-Cat", item_name="P213-A-Item"
    )
    cat_b, item_b, bill_b = _seed_bill(
        client, owner_b, cat_name="P213-B-Cat", item_name="P213-B-Item"
    )

    # --- Categories ---
    assert client.get(f"/api/v1/categories/{cat_b}", headers=owner_a).status_code == 404
    assert client.get(f"/api/v1/categories/{cat_a}", headers=owner_b).status_code == 404
    cats_a = {c["id"] for c in client.get("/api/v1/categories", headers=owner_a).get_json()["data"]}
    cats_b = {c["id"] for c in client.get("/api/v1/categories", headers=owner_b).get_json()["data"]}
    assert cat_b not in cats_a and cat_a not in cats_b

    # --- Items ---
    assert client.get(f"/api/v1/items/{item_b['id']}", headers=owner_a).status_code == 404
    assert client.get(f"/api/v1/items/{item_a['id']}", headers=owner_b).status_code == 404
    items_a = {i["id"] for i in client.get("/api/v1/items", headers=owner_a).get_json()["data"]}
    assert item_b["id"] not in items_a

    # Cannot bill using other tenant's item
    bad_bill = client.post(
        "/api/v1/bills",
        headers=owner_a,
        json={"items": [{"item_id": item_b["id"], "quantity": 1}]},
    )
    assert bad_bill.status_code in {400, 404}

    # --- Bills ---
    assert client.get(f"/api/v1/bills/{bill_b['id']}", headers=owner_a).status_code == 404
    assert client.get(f"/api/v1/bills/{bill_a['id']}", headers=owner_b).status_code == 404
    assert (
        client.post(
            f"/api/v1/bills/{bill_b['id']}/cancel",
            headers=owner_a,
            json={"reason": "cross-tenant probe"},
        ).status_code
        == 404
    )

    # --- Reports (tenant-scoped; bill numbers may collide across tenants — use bill id) ---
    bills_a = {
        b["id"]
        for b in client.get("/api/v1/bills", headers=owner_a).get_json()["data"]
    }
    bills_b = {
        b["id"]
        for b in client.get("/api/v1/bills", headers=owner_b).get_json()["data"]
    }
    assert bill_a["id"] in bills_a and bill_b["id"] not in bills_a
    assert bill_b["id"] in bills_b and bill_a["id"] not in bills_b

    summary_a = client.get(
        "/api/v1/reports/summary",
        headers=owner_a,
        query_string={"period": "today"},
    ).get_json()["data"]["current"]
    summary_b = client.get(
        "/api/v1/reports/summary",
        headers=owner_b,
        query_string={"period": "today"},
    ).get_json()["data"]["current"]
    assert summary_a["total_sales"] >= float(bill_a["grand_total"])
    assert summary_b["total_sales"] >= float(bill_b["grand_total"])

    # --- Users ---
    users_a = client.get("/api/v1/users", headers=owner_a).get_json()["data"]
    users_b = client.get("/api/v1/users", headers=owner_b).get_json()["data"]
    assert "owner@hotelb.com" not in {u["email"] for u in users_a}
    assert "owner@hotela.com" not in {u["email"] for u in users_b}
    user_b_id = next(u["id"] for u in users_b if u["email"] == "owner@hotelb.com")
    assert client.get(f"/api/v1/users/{user_b_id}", headers=owner_a).status_code == 404

    # --- Audit / item activity (match by entity_id / bill id — not display bill_number) ---
    activity_a = client.get(
        "/api/v1/audit-logs",
        headers=owner_a,
        query_string={"entity_type": "ITEM", "entity_id": item_a["id"]},
    ).get_json()["data"]
    assert any(r["action"] == "ITEM_CREATED" for r in activity_a)

    create_a = next(r for r in activity_a if r["action"] == "ITEM_CREATED")
    assert client.get(f"/api/v1/audit-logs/{create_a['id']}", headers=owner_b).status_code == 404

    creates_a = client.get(
        "/api/v1/audit-logs",
        headers=owner_a,
        query_string={"action": "CREATE_BILL"},
    ).get_json()["data"]
    assert any(r.get("entity_id") == bill_a["id"] for r in creates_a)
    assert not any(r.get("entity_id") == bill_b["id"] for r in creates_a)

    creates_b = client.get(
        "/api/v1/audit-logs",
        headers=owner_b,
        query_string={"action": "CREATE_BILL"},
    ).get_json()["data"]
    assert any(r.get("entity_id") == bill_b["id"] for r in creates_b)
    assert not any(r.get("entity_id") == bill_a["id"] for r in creates_b)
