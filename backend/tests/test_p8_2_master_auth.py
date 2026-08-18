"""P8-2: Master Admin authentication is separate from tenant Owner/Billing."""

from app.models.master_admin import ROLE_MASTER_ADMIN, MasterAdmin
from app.utils.security import hash_password
from tests.conftest import login


def _seed_master(app, *, email="master@prabhatech.test", active=True):
    from app.extensions import db

    with app.app_context():
        admin = MasterAdmin(
            id="m1111111-1111-1111-1111-111111111111",
            name="Prabha Technology Admin",
            email=email,
            password_hash=hash_password("Master@12345"),
            is_active=active,
            token_version=0,
        )
        db.session.add(admin)
        db.session.commit()
    return email


def test_master_login_has_no_tenant_claim(client, app):
    _seed_master(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "master@prabhatech.test", "password": "Master@12345"},
    )
    assert response.status_code == 200, response.get_json()
    payload = response.get_json()["data"]
    assert payload["user"]["role"] == ROLE_MASTER_ADMIN
    assert payload["user"]["tenant"] is None
    assert payload["user"]["email"] == "master@prabhatech.test"


def test_owner_cannot_access_master_dashboard_api(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/master/dashboard/summary", headers=owner)
    assert response.status_code == 403
    assert response.get_json()["error"]["code"] == "FORBIDDEN"


def test_billing_user_cannot_access_master_dashboard_api(client):
    billing = login(client, "billing@hotela.com", "Billing@12345")
    response = client.get("/api/v1/master/dashboard/summary", headers=billing)
    assert response.status_code == 403


def test_master_cannot_access_tenant_bill_list(client, app):
    _seed_master(app)
    headers = login(client, "master@prabhatech.test", "Master@12345")
    response = client.get("/api/v1/bills", headers=headers)
    assert response.status_code == 403
    assert "tenant" in (response.get_json()["error"]["message"] or "").lower()


def test_master_dashboard_summary_uses_real_tenant_counts(client, app):
    _seed_master(app)
    headers = login(client, "master@prabhatech.test", "Master@12345")
    response = client.get("/api/v1/master/dashboard/summary", headers=headers)
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert data["total_businesses"] == 2
    assert data["active_businesses"] == 2
    assert data["suspended_businesses"] == 0


def test_inactive_master_cannot_login(client, app):
    _seed_master(app, email="inactive-master@prabhatech.test", active=False)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive-master@prabhatech.test", "password": "Master@12345"},
    )
    assert response.status_code == 401


def test_master_logout_revokes_token(client, app):
    _seed_master(app)
    headers = login(client, "master@prabhatech.test", "Master@12345")
    assert client.get("/api/v1/master/dashboard/summary", headers=headers).status_code == 200
    logout = client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 200
    again = client.get("/api/v1/master/dashboard/summary", headers=headers)
    assert again.status_code == 401


def test_unauthenticated_master_summary_is_401(client):
    response = client.get("/api/v1/master/dashboard/summary")
    assert response.status_code == 401
