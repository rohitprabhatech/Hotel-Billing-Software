"""Sprint 20 gap coverage: suspended tenant, bill validation, registration edges, settings."""

from app.extensions import db
from app.models.tenant import Tenant
from tests.conftest import login


def _menu_item(client, headers, *, name="Gap Item", sku=None, price=100):
    category_id = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": f"Cat-{name}"},
    ).get_json()["data"]["id"]
    payload = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "gst_percentage": 5,
    }
    if sku is not None:
        payload["sku"] = sku
    return client.post("/api/v1/items", headers=headers, json=payload).get_json()["data"]


def test_suspended_tenant_blocks_login_and_authenticated_calls(client, app):
    headers = login(client, "owner@hotela.com", "Owner@12345")

    with app.app_context():
        tenant = db.session.get(Tenant, "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        tenant.status = "SUSPENDED"
        db.session.commit()

    # Existing JWT is rejected once tenant is suspended
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 401
    me_message = (me.get_json().get("error") or {}).get("message", "").lower()
    assert "suspend" in me_message

    # Fresh login also fails (generic credentials message by design)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@hotela.com", "password": "Owner@12345"},
    )
    assert response.status_code == 401


def test_discount_cannot_exceed_subtotal_via_api(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _menu_item(client, owner, price=100)

    response = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "reference": "DISC-1",
            "discount": 500,
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    )
    assert response.status_code == 400


def test_bill_rejects_zero_negative_qty_and_empty_cart(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _menu_item(client, owner, name="Qty Guard")

    empty = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": []},
    )
    assert empty.status_code == 400

    zero = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": 0}]},
    )
    assert zero.status_code == 400

    negative = client.post(
        "/api/v1/bills",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": -1}]},
    )
    assert negative.status_code == 400


def test_duplicate_line_items_are_merged(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _menu_item(client, owner, name="Merge Item", price=50)

    response = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "reference": "MERGE-1",
            "items": [
                {"item_id": item["id"], "quantity": 1},
                {"item_id": item["id"], "quantity": 2},
            ],
        },
    )
    assert response.status_code == 201, response.get_json()
    bill = response.get_json()["data"]
    assert len(bill["items"]) == 1
    assert bill["items"][0]["quantity"] == 3
    assert bill["subtotal"] == 150.0


def test_register_other_and_invalid_business_type(client):
    ok = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Generic Shop",
            "business_type": "other",
            "owner_name": "Gen Owner",
            "owner_email": "owner@generic.shop",
            "password": "Generic@12345",
            "confirm_password": "Generic@12345",
        },
    )
    assert ok.status_code == 201, ok.get_json()
    assert ok.get_json()["data"]["business_type"] == "other"

    bad = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Spaceship Mart",
            "business_type": "spaceship",
            "owner_name": "Alien",
            "owner_email": "owner@spaceship.shop",
            "password": "Alien@12345",
            "confirm_password": "Alien@12345",
        },
    )
    assert bad.status_code == 400


def test_register_defaults_business_type_to_other(client):
    response = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Default Type Shop",
            "owner_name": "Default Owner",
            "owner_email": "owner@defaulttype.shop",
            "password": "Default@12345",
            "confirm_password": "Default@12345",
        },
    )
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["data"]["business_type"] == "other"


def test_owner_updates_tenant_settings_fields(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    updated = client.put(
        "/api/v1/tenants/me",
        headers=owner,
        json={
            "business_name": "Hotel A Deluxe",
            "address": "FC Road",
            "city": "Pune",
            "gst_number": "27AAAAA0000A1Z5",
            "bill_number_prefix": "HA-",
        },
    )
    assert updated.status_code == 200, updated.get_json()
    data = updated.get_json()["data"]
    assert data["business_name"] == "Hotel A Deluxe"
    assert data["address"] == "FC Road"
    assert data["city"] == "Pune"
    assert data["gst_number"] == "27AAAAA0000A1Z5"
    assert data["bill_number_prefix"] == "HA-"

    fetched = client.get("/api/v1/tenants/me", headers=owner)
    assert fetched.status_code == 200
    again = fetched.get_json()["data"]
    assert again["business_name"] == "Hotel A Deluxe"
    assert again["bill_number_prefix"] == "HA-"


def test_sku_uniqueness_is_tenant_scoped(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    item_a = _menu_item(client, owner_a, name="SKU A", sku="SHARED-SKU")
    assert item_a["sku"]

    dup_a = client.post(
        "/api/v1/items",
        headers=owner_a,
        json={
            "name": "SKU A Dup",
            "category_id": item_a["category_id"],
            "price": 10,
            "gst_percentage": 5,
            "sku": "shared-sku",
        },
    )
    assert dup_a.status_code == 409

    item_b = _menu_item(client, owner_b, name="SKU B", sku="SHARED-SKU")
    assert item_b["sku"].upper() == "SHARED-SKU"


def test_billing_user_blocked_from_weekly_and_export(client):
    billing = login(client, "billing@hotela.com", "Billing@12345")
    weekly = client.get("/api/v1/reports/weekly-sales", headers=billing)
    assert weekly.status_code == 403
    export = client.get(
        "/api/v1/reports/export?report_type=daily&format=csv",
        headers=billing,
    )
    assert export.status_code == 403
