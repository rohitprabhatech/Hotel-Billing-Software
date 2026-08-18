"""P8-3: public registration stays PENDING until Master Admin approve/reject."""

from app.extensions import db
from app.models.registration_request import REGISTRATION_APPROVED, REGISTRATION_PENDING
from app.models.tenant import Tenant
from app.models.user import User
from app.services.email_service import EmailService
from tests.conftest import login, login_master, seed_master_admin


def _register(client, **overrides):
    payload = {
        "business_name": "Sunrise Inn Pvt Ltd",
        "business_type": "hotel",
        "address": "MG Road",
        "city": "Pune",
        "mobile": "9876543210",
        "owner_name": "Ramesh",
        "owner_email": "owner@sunrise.test",
        "password": "Sunrise@12345",
        "confirm_password": "Sunrise@12345",
        "terms_accepted": True,
    }
    payload.update(overrides)
    return client.post("/api/v1/auth/register-business", json=payload)


def test_register_does_not_create_tenant_or_allow_login(client):
    EmailService.clear_outbox()
    response = _register(client)
    assert response.status_code == 201, response.get_json()
    body = response.get_json()["data"]
    assert "tenant_id" not in body
    assert "verification_token" not in body
    assert body["status"] == REGISTRATION_PENDING
    assert "submitted successfully" in body["message"]
    assert "Prabha Technology" in body["message"]
    assert body["business_type"] == "hotel"

    outbox = EmailService.get_outbox()
    assert outbox
    assert "received" in outbox[0]["subject"].lower() or "registration" in outbox[0]["subject"].lower()

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@sunrise.test", "password": "Sunrise@12345"},
    )
    assert blocked.status_code == 401
    assert "pending approval" in (blocked.get_json()["error"]["message"] or "").lower()


def test_terms_accepted_required(client):
    response = _register(client, terms_accepted=False, owner_email="noterms@test.com")
    assert response.status_code == 400


def test_pending_duplicate_email_rejected(client):
    assert _register(client).status_code == 201
    again = _register(client)
    assert again.status_code == 409


def test_owner_cannot_list_registration_requests(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/master/registration-requests", headers=owner)
    assert response.status_code == 403


def test_master_lists_pending_and_detail_omits_password(client, app):
    created = _register(client)
    request_id = created.get_json()["data"]["request_id"]
    headers = login_master(client, app)

    listed = client.get("/api/v1/master/registration-requests?status=PENDING", headers=headers)
    assert listed.status_code == 200, listed.get_json()
    rows = listed.get_json()["data"]
    assert any(row["id"] == request_id for row in rows)
    assert all("password" not in row and "password_hash" not in row for row in rows)

    detail = client.get(f"/api/v1/master/registration-requests/{request_id}", headers=headers)
    assert detail.status_code == 200
    data = detail.get_json()["data"]
    assert data["owner_email"] == "owner@sunrise.test"
    assert "password_hash" not in data
    assert "password" not in data


def test_approve_creates_active_tenant_and_owner_can_login(client, app):
    EmailService.clear_outbox()
    created = _register(client)
    request_id = created.get_json()["data"]["request_id"]
    headers = login_master(client, app)

    approved = client.post(
        f"/api/v1/master/registration-requests/{request_id}/approve",
        headers=headers,
    )
    assert approved.status_code == 200, approved.get_json()
    data = approved.get_json()["data"]
    assert data["status"] == REGISTRATION_APPROVED
    assert data["tenant_id"]
    assert "password_hash" not in data

    ok = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@sunrise.test", "password": "Sunrise@12345"},
    )
    assert ok.status_code == 200, ok.get_json()
    user = ok.get_json()["data"]["user"]
    assert user["role"] == "OWNER"
    assert user["email_verified"] is True
    assert user["tenant"]["status"] == "ACTIVE"
    assert user["tenant"]["business_name"] == "Sunrise Inn Pvt Ltd"

    subjects = [mail["subject"].lower() for mail in EmailService.get_outbox()]
    assert any("approved" in subject for subject in subjects)

    again = client.post(
        f"/api/v1/master/registration-requests/{request_id}/approve",
        headers=headers,
    )
    assert again.status_code == 400


def test_reject_requires_reason_and_allows_reapply(client, app):
    EmailService.clear_outbox()
    created = _register(client)
    request_id = created.get_json()["data"]["request_id"]
    headers = login_master(client, app)

    missing = client.post(
        f"/api/v1/master/registration-requests/{request_id}/reject",
        headers=headers,
        json={},
    )
    assert missing.status_code == 400

    short = client.post(
        f"/api/v1/master/registration-requests/{request_id}/reject",
        headers=headers,
        json={"reason": "short"},
    )
    assert short.status_code == 400

    rejected = client.post(
        f"/api/v1/master/registration-requests/{request_id}/reject",
        headers=headers,
        json={"reason": "Incomplete business details provided"},
    )
    assert rejected.status_code == 200, rejected.get_json()
    assert rejected.get_json()["data"]["status"] == "REJECTED"
    assert rejected.get_json()["data"]["tenant_id"] is None

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@sunrise.test", "password": "Sunrise@12345"},
    )
    assert blocked.status_code == 401

    reapply = _register(client)
    assert reapply.status_code == 201, reapply.get_json()


def test_seeded_owner_still_logs_in_without_approval(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.get_json()["data"]["role"] == "OWNER"


def test_dashboard_pending_requests_count(client, app):
    seed_master_admin(app)
    headers = login(client, "master@prabhatech.test", "Master@12345")
    before = client.get("/api/v1/master/dashboard/summary", headers=headers).get_json()["data"]
    assert before["pending_requests"] == 0
    _register(client)
    after = client.get("/api/v1/master/dashboard/summary", headers=headers).get_json()["data"]
    assert after["pending_requests"] == 1
    assert after["total_businesses"] == 2


def test_approve_does_not_leave_unverified_owner(client, app):
    created = _register(client, owner_email="ready@shop.test")
    request_id = created.get_json()["data"]["request_id"]
    headers = login_master(client, app)
    client.post(f"/api/v1/master/registration-requests/{request_id}/approve", headers=headers)
    with app.app_context():
        user = db.session.query(User).filter_by(email="ready@shop.test").one()
        tenant = db.session.query(Tenant).filter_by(id=user.tenant_id).one()
        assert user.email_verified is True
        assert tenant.status == "ACTIVE"
