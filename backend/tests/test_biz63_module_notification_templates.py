"""Sprint BIZ-63 — module notification templates."""

from app.constants.notification_templates import NOTIFICATION_TEMPLATES, list_templates
from app.services.notification_service import NotificationService
from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name):
    response = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": name,
            "category_id": category_id,
            "price": "120",
            "gst_percentage": "5",
            "stock_quantity": "50",
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_registry_has_at_least_five_industry_templates():
    industry = [k for k, v in NOTIFICATION_TEMPLATES.items() if v.get("industry")]
    assert len(industry) >= 5
    required = {
        "kot_ready",
        "repair_ready",
        "batch_expiring",
        "travel_payment_due",
        "credit_due",
    }
    assert required.issubset(set(industry))


def test_templates_catalog_api_module_filtered(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")

    response = client.get("/api/v1/notifications/templates", headers=owner)
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    keys = {row["key"] for row in data["templates"]}
    assert "kot_ready" in keys
    assert "low_stock" in keys
    assert data["industry_count"] >= 1

    industry_only = client.get(
        "/api/v1/notifications/templates",
        headers=owner,
        query_string={"industry_only": "true"},
    )
    assert industry_only.status_code == 200
    only_keys = {row["key"] for row in industry_only.get_json()["data"]["templates"]}
    assert "kot_ready" in only_keys
    assert "low_stock" not in only_keys

    _switch(client, owner, "clothing")
    clothing = client.get("/api/v1/notifications/templates", headers=owner)
    clothing_keys = {row["key"] for row in clothing.get_json()["data"]["templates"]}
    assert "kot_ready" not in clothing_keys
    assert "low_stock" in clothing_keys


def test_kot_ready_emits_and_dedupes_open_alert(app, client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, headers, "hotel_restaurant")
    tenant_id = client.get("/api/v1/tenants/me", headers=headers).get_json()["data"]["id"]

    cat_id = _category(client, headers, "BIZ63 KOT Cat")
    item = _item(client, headers, cat_id, "BIZ63 KOT Item")
    order = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "customer_name": "BIZ63 Guest",
            "items": [{"item_id": item["id"], "quantity": "1"}],
        },
    ).get_json()["data"]
    kot = client.post(
        f"/api/v1/orders/{order['id']}/kot", headers=headers
    ).get_json()["data"]

    ready = client.patch(
        f"/api/v1/kots/{kot['id']}/status",
        headers=headers,
        json={"status": "ready"},
    )
    assert ready.status_code == 200, ready.get_json()

    notes = client.get(
        "/api/v1/notifications", headers=headers, query_string={"per_page": 100}
    )
    assert notes.status_code == 200
    kot_notes = [
        row
        for row in notes.get_json()["data"]
        if row["type"] == "KOT_READY" and row["entity_id"] == kot["id"]
    ]
    assert len(kot_notes) == 1
    assert "ready" in kot_notes[0]["message"].lower()

    with app.app_context():
        suppressed = NotificationService.emit_template(
            key="kot_ready",
            tenant_id=tenant_id,
            entity_id=kot["id"],
            context={
                "kot_number": kot["kot_number"],
                "order_number": order.get("order_number") or "—",
                "table_part": "",
            },
        )
        assert suppressed is None

    notes2 = client.get(
        "/api/v1/notifications", headers=headers, query_string={"per_page": 100}
    )
    kot_notes2 = [
        row
        for row in notes2.get_json()["data"]
        if row["type"] == "KOT_READY" and row["entity_id"] == kot["id"]
    ]
    assert len(kot_notes2) == 1


def test_emit_template_cooldown_rate_limit(app, client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    tenant_id = client.get("/api/v1/tenants/me", headers=owner).get_json()["data"]["id"]

    with app.app_context():
        first = NotificationService.emit_template(
            key="travel_payment_due",
            tenant_id=tenant_id,
            entity_id="TB-BIZ63-TEST",
            context={
                "booking_number": "TB-BIZ63-TEST",
                "customer_name": "Cooldown Guest",
                "remaining": 1500.0,
            },
        )
        assert first is not None
        second = NotificationService.emit_template(
            key="travel_payment_due",
            tenant_id=tenant_id,
            entity_id="TB-BIZ63-TEST",
            context={
                "booking_number": "TB-BIZ63-TEST",
                "customer_name": "Cooldown Guest",
                "remaining": 1500.0,
            },
        )
        assert second is None


def test_templates_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "hotel_restaurant")
    _switch(client, owner_b, "clothing")

    a = client.get("/api/v1/notifications/templates", headers=owner_a).get_json()["data"]
    b = client.get("/api/v1/notifications/templates", headers=owner_b).get_json()["data"]
    assert "kot_ready" in {row["key"] for row in a["templates"]}
    assert "kot_ready" not in {row["key"] for row in b["templates"]}
    assert set(a["enabled_modules"]) != set(b["enabled_modules"])


def test_catalog_serialize_matches_registry():
    rows = list_templates()
    assert len(rows) == len(NOTIFICATION_TEMPLATES)
    by_key = {row["key"]: row for row in rows}
    assert by_key["repair_ready"]["type"] == "REPAIR_READY"
    assert by_key["batch_expired"]["dedupe_open"] is True
