"""Authentication and authorization tests."""

from tests.conftest import login


def test_login_owner_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@hotela.com", "password": "Owner@12345"},
    )
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["token_type"] == "Bearer"
    assert data["user"]["role"] == "OWNER"
    assert data["user"]["tenant"]["business_name"] == "Hotel A"
    assert "password_hash" not in data["user"]


def test_login_billing_user_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "billing@hotela.com", "password": "Billing@12345"},
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["user"]["role"] == "BILLING_USER"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@hotela.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_token(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["email"] == "owner@hotela.com"


def test_billing_user_forbidden_from_users_api(client):
    headers = login(client, "billing@hotela.com", "Billing@12345")
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 403


def test_owner_can_list_users(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    emails = {u["email"] for u in response.get_json()["data"]}
    assert "owner@hotela.com" in emails
    assert "billing@hotela.com" in emails
    assert "owner@hotelb.com" not in emails


def test_owner_can_create_billing_user(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "Counter 2",
            "email": "counter2@hotela.com",
            "password": "Billing@12345",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["data"]["role"] == "BILLING_USER"


def test_logout(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
