"""Business registration, Master approval, password reset/change tests."""

from app.services.email_service import EmailService
from tests.conftest import login, login_master


def test_register_approve_login_flow(client, app):
    EmailService.clear_outbox()
    response = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Sunrise Inn Pvt Ltd",
            "business_type": "hotel_restaurant",
            "address": "MG Road",
            "city": "Pune",
            "mobile": "9876543210",
            "owner_name": "Ramesh",
            "owner_email": "owner@sunrise.test",
            "password": "Sunrise@12345",
            "confirm_password": "Sunrise@12345",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 201, response.get_json()
    body = response.get_json()["data"]
    assert body["status"] == "PENDING"
    assert "tenant_id" not in body
    assert "verification_token" not in body
    assert body["business_type"] == "hotel_restaurant"
    outbox = EmailService.get_outbox()
    assert outbox
    assert "registration" in outbox[0]["subject"].lower() or "received" in outbox[0]["subject"].lower()

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@sunrise.test", "password": "Sunrise@12345"},
    )
    assert blocked.status_code == 401

    master = login_master(client, app)
    approved = client.post(
        f"/api/v1/master/registration-requests/{body['request_id']}/approve",
        headers=master,
    )
    assert approved.status_code == 200, approved.get_json()

    ok = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@sunrise.test", "password": "Sunrise@12345"},
    )
    assert ok.status_code == 200
    assert ok.get_json()["data"]["user"]["role"] == "OWNER"
    assert ok.get_json()["data"]["user"]["tenant"]["business_name"] == "Sunrise Inn Pvt Ltd"
    assert ok.get_json()["data"]["user"]["tenant"]["business_type"] == "hotel_restaurant"
    assert ok.get_json()["data"]["user"]["tenant"]["business_type_label"] == "Hotels / Restaurants"


def test_legacy_register_hotel_alias_still_works(client):
    response = client.post(
        "/api/v1/auth/register-hotel",
        json={
            "hotel_name": "Legacy Cafe",
            "business_name": "Legacy Cafe",
            "business_type": "cafe_tea",
            "owner_name": "Legacy Owner",
            "owner_email": "legacy@cafe.test",
            "password": "Legacy@12345",
            "confirm_password": "Legacy@12345",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["data"]["business_type"] == "cafe_tea"


def test_register_duplicate_email_rejected(client):
    payload = {
        "business_name": "Hotel Dup",
        "business_type": "hotel_restaurant",
        "owner_name": "Dup",
        "owner_email": "owner@hotela.com",
        "password": "DupPass@123",
        "confirm_password": "DupPass@123",
        "terms_accepted": True,
    }
    response = client.post("/api/v1/auth/register-business", json=payload)
    assert response.status_code == 409


def test_change_password_and_revoke_old_token(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    changed = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "current_password": "Owner@12345",
            "new_password": "Owner@99999",
            "confirm_password": "Owner@99999",
        },
    )
    assert changed.status_code == 200

    stale = client.get("/api/v1/auth/me", headers=headers)
    assert stale.status_code == 401

    headers2 = login(client, "owner@hotela.com", "Owner@99999")
    me = client.get("/api/v1/auth/me", headers=headers2)
    assert me.status_code == 200


def test_forgot_and_reset_password(client):
    EmailService.clear_outbox()
    forgot = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "billing@hotela.com"},
    )
    assert forgot.status_code == 200
    reset_token = forgot.get_json()["data"]["reset_token"]

    reset = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "password": "Billing@99999",
            "confirm_password": "Billing@99999",
        },
    )
    assert reset.status_code == 200

    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "billing@hotela.com", "password": "Billing@12345"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "billing@hotela.com", "password": "Billing@99999"},
        ).status_code
        == 200
    )


def test_registered_tenants_are_isolated(client, app):
    r1 = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Iso A",
            "business_type": "clothing",
            "mobile": "9000000001",
            "owner_name": "Iso Owner A",
            "owner_email": "iso-a@test.com",
            "password": "IsoPass@123",
            "confirm_password": "IsoPass@123",
            "terms_accepted": True,
        },
    )
    r2 = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Iso B",
            "business_type": "grocery_kirana",
            "mobile": "9000000002",
            "owner_name": "Iso Owner B",
            "owner_email": "iso-b@test.com",
            "password": "IsoPass@123",
            "confirm_password": "IsoPass@123",
            "terms_accepted": True,
        },
    )
    assert r1.status_code == 201 and r2.status_code == 201, (r1.get_json(), r2.get_json())
    master = login_master(client, app)
    assert (
        client.post(
            f"/api/v1/master/registration-requests/{r1.get_json()['data']['request_id']}/approve",
            headers=master,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/master/registration-requests/{r2.get_json()['data']['request_id']}/approve",
            headers=master,
        ).status_code
        == 200
    )

    headers_a = login(client, "iso-a@test.com", "IsoPass@123")
    tenant_a = client.get("/api/v1/tenants/me", headers=headers_a).get_json()["data"]
    headers_b = login(client, "iso-b@test.com", "IsoPass@123")
    tenant_b = client.get("/api/v1/tenants/me", headers=headers_b).get_json()["data"]
    assert tenant_a["id"] != tenant_b["id"]
    assert tenant_a["business_name"] == "Iso A"
    assert tenant_b["business_name"] == "Iso B"
    assert tenant_a["business_type"] == "clothing"
    assert tenant_b["business_type"] == "grocery_kirana"


def test_profile_update(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.put(
        "/api/v1/profile",
        headers=headers,
        json={"name": "Owner A Updated", "phone": "9000011111"},
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == "Owner A Updated"
