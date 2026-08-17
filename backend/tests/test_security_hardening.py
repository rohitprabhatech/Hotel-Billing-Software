"""Sprint 21 security hardening tests — session revoke, email uniqueness, IDOR, tokens."""

from app.extensions import db
from app.models.auth_token import PasswordResetToken
from app.models.user import User
from app.services.email_service import EmailService
from tests.conftest import login


def _create_item(client, headers, name="Sec Item"):
    category_id = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": f"Sec-{name}"},
    ).get_json()["data"]["id"]
    return client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": name,
            "category_id": category_id,
            "price": 100,
            "gst_percentage": 5,
        },
    ).get_json()["data"]


def test_logout_revokes_existing_jwt(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    logged_out = client.post("/api/v1/auth/logout", headers=headers)
    assert logged_out.status_code == 200

    stale = client.get("/api/v1/auth/me", headers=headers)
    assert stale.status_code == 401


def test_deactivate_user_rejects_existing_jwt(client, app):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    assert client.get("/api/v1/auth/me", headers=billing).status_code == 200

    with app.app_context():
        user = (
            db.session.query(User)
            .filter(User.email == "billing@hotela.com")
            .first()
        )
        billing_id = user.id

    deactivated = client.put(
        f"/api/v1/users/{billing_id}",
        headers=owner,
        json={"is_active": False},
    )
    assert deactivated.status_code == 200, deactivated.get_json()

    stale = client.get("/api/v1/auth/me", headers=billing)
    assert stale.status_code == 401


def test_cannot_create_billing_user_with_email_from_other_tenant(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    response = client.post(
        "/api/v1/users",
        headers=owner_a,
        json={
            "name": "Collision",
            "email": "owner@hotelb.com",
            "password": "Collision@123",
        },
    )
    assert response.status_code == 409


def test_bill_rejects_other_tenant_item_id(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    item_b = _create_item(client, owner_b, name="B-only")

    response = client.post(
        "/api/v1/bills",
        headers=owner_a,
        json={"items": [{"item_id": item_b["id"], "quantity": 1}]},
    )
    assert response.status_code == 400


def test_item_get_other_tenant_returns_404(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    item_b = _create_item(client, owner_b, name="Hidden")

    response = client.get(f"/api/v1/items/{item_b['id']}", headers=owner_a)
    assert response.status_code == 404


def test_forgot_password_invalidates_previous_unused_tokens(client, app):
    EmailService.clear_outbox()
    first = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "owner@hotela.com"},
    )
    assert first.status_code == 200
    first_token = first.get_json()["data"].get("reset_token")
    assert first_token

    second = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "owner@hotela.com"},
    )
    assert second.status_code == 200
    second_token = second.get_json()["data"].get("reset_token")
    assert second_token
    assert second_token != first_token

    with app.app_context():
        unused = (
            db.session.query(PasswordResetToken)
            .filter(PasswordResetToken.used_at.is_(None))
            .count()
        )
        # Only the latest unused token should remain usable
        assert unused == 1

    # Old token rejected
    old_use = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": first_token,
            "password": "Owner@New111",
            "confirm_password": "Owner@New111",
        },
    )
    assert old_use.status_code == 400

    # New token works
    new_use = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": second_token,
            "password": "Owner@New222",
            "confirm_password": "Owner@New222",
        },
    )
    assert new_use.status_code == 200, new_use.get_json()
    login(client, "owner@hotela.com", "Owner@New222")


def test_audit_put_and_delete_not_allowed(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    listed = client.get("/api/v1/audit-logs", headers=owner)
    assert listed.status_code == 200
    rows = listed.get_json().get("data") or []
    if not rows:
        # Ensure at least one audit row via login already happened
        return
    audit_id = rows[0]["id"]
    assert client.put(f"/api/v1/audit-logs/{audit_id}", headers=owner).status_code in {
        404,
        405,
    }
    assert client.delete(f"/api/v1/audit-logs/{audit_id}", headers=owner).status_code in {
        404,
        405,
    }


def test_client_supplied_unit_price_ignored_on_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    item = _create_item(client, owner, name="Priced")
    response = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [
                {
                    "item_id": item["id"],
                    "quantity": 1,
                    "unit_price": 1,
                    "item_name": "Hacked",
                }
            ],
            "grand_total": 1,
        },
    )
    assert response.status_code == 201, response.get_json()
    bill = response.get_json()["data"]
    assert bill["items"][0]["unit_price"] == 100.0
    assert bill["items"][0]["item_name"] == "Priced"
    assert bill["grand_total"] != 1.0
