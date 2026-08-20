"""Sprint 5: Master business activate/deactivate/suspend + platform audit."""

from app.extensions import db
from app.models.platform_audit_log import PlatformAuditLog
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.request_context import MasterContext, set_master_context
from tests.conftest import login
from tests.test_p8_4_trial_management import _approve
from tests.test_p8_5_plan_management import _create_plan


def test_owner_cannot_activate_or_read_platform_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    tenant_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    assert (
        client.post(f"/api/v1/master/businesses/{tenant_id}/deactivate", headers=owner).status_code
        == 403
    )
    assert client.get("/api/v1/master/audit-logs", headers=owner).status_code == 403


def test_deactivate_blocks_login_and_keeps_data(client, app):
    approved, master = _approve(client, app, email="lifecycle-off@shop.test")
    tenant_id = approved.get_json()["data"]["tenant_id"]
    owner_headers = login(client, "lifecycle-off@shop.test", "Trial@12345")

    deactivated = client.post(
        f"/api/v1/master/businesses/{tenant_id}/deactivate",
        headers=master,
    )
    assert deactivated.status_code == 200, deactivated.get_json()
    assert deactivated.get_json()["data"]["tenant_status"] == "SUSPENDED"

    me = client.get("/api/v1/auth/me", headers=owner_headers)
    assert me.status_code == 401
    assert "suspend" in (me.get_json()["error"]["message"] or "").lower()

    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "lifecycle-off@shop.test", "password": "Trial@12345"},
    )
    assert blocked.status_code == 401

    with app.app_context():
        tenant = db.session.get(Tenant, tenant_id)
        owner = db.session.query(User).filter_by(email="lifecycle-off@shop.test").one()
        assert tenant is not None
        assert tenant.status == "SUSPENDED"
        assert owner is not None

    restored = client.post(
        f"/api/v1/master/businesses/{tenant_id}/activate",
        headers=master,
    )
    assert restored.status_code == 200, restored.get_json()
    assert restored.get_json()["data"]["tenant_status"] == "ACTIVE"
    login(client, "lifecycle-off@shop.test", "Trial@12345")


def test_suspend_allows_login_but_locks_billing(client, app):
    approved, master = _approve(client, app, email="lifecycle-suspend@shop.test")
    tenant_id = approved.get_json()["data"]["tenant_id"]

    suspended = client.post(
        f"/api/v1/master/businesses/{tenant_id}/suspend",
        headers=master,
    )
    assert suspended.status_code == 200, suspended.get_json()
    assert suspended.get_json()["data"]["status"] == "SUSPENDED"
    assert suspended.get_json()["data"]["access_allowed"] is False

    owner = login(client, "lifecycle-suspend@shop.test", "Trial@12345")
    me = client.get("/api/v1/auth/me", headers=owner)
    assert me.status_code == 200
    assert me.get_json()["data"]["tenant"]["status"] == "ACTIVE"
    assert me.get_json()["data"]["tenant"]["subscription"]["status"] == "SUSPENDED"

    blocked = client.get("/api/v1/bills", headers=owner)
    assert blocked.status_code == 402
    profile = client.get("/api/v1/profile", headers=owner)
    assert profile.status_code == 200

    resumed = client.post(
        f"/api/v1/master/businesses/{tenant_id}/unsuspend",
        headers=master,
    )
    assert resumed.status_code == 200, resumed.get_json()
    assert resumed.get_json()["data"]["access_allowed"] is True
    assert client.get("/api/v1/bills", headers=owner).status_code == 200


def test_platform_audit_records_master_actions_without_secrets(client, app):
    approved, master = _approve(client, app, email="audit-biz@shop.test")
    tenant_id = approved.get_json()["data"]["tenant_id"]
    request_id = approved.get_json()["data"]["id"]

    created = _create_plan(client, master, name="Audit Plan", price=550)
    plan_id = created.get_json()["data"]["id"]
    client.put(
        f"/api/v1/master/plans/{plan_id}",
        headers=master,
        json={"price": 650},
    )
    client.put(
        "/api/v1/master/settings/trial",
        headers=master,
        json={"trial_enabled": True, "trial_days": 20, "expiry_warning_days": 5},
    )
    client.post(
        f"/api/v1/master/businesses/{tenant_id}/deactivate",
        headers=master,
    )

    listed = client.get("/api/v1/master/audit-logs?per_page=50", headers=master)
    assert listed.status_code == 200, listed.get_json()
    rows = listed.get_json()["data"]
    actions = {row["action"] for row in rows}
    assert "BUSINESS_APPROVED" in actions
    assert "PLAN_CREATED" in actions
    assert "PLAN_UPDATED" in actions
    assert "TRIAL_SETTINGS_UPDATED" in actions
    assert "BUSINESS_DEACTIVATED" in actions
    assert any(row["entity_id"] == request_id or row["tenant_id"] == tenant_id for row in rows)
    for row in rows:
        blob = f"{row.get('old_data')}{row.get('new_data')}".lower()
        assert "password" not in blob
        assert "token" not in blob

    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert client.get("/api/v1/master/audit-logs", headers=owner).status_code == 403

    with app.app_context():
        with app.test_request_context():
            set_master_context(
                MasterContext(
                    admin_id=None,
                    role="MASTER_ADMIN",
                    name="Scrub Test",
                    email="master@prabhatech.test",
                )
            )
            from app.services.platform_audit_service import PlatformAuditService

            PlatformAuditService.log(
                action="PLAN_UPDATED",
                entity_type="SUBSCRIPTION_PLAN",
                new_data={"name": "safe", "password": "secret", "access_token": "abc"},
            )
            db.session.commit()
            row = (
                db.session.query(PlatformAuditLog)
                .filter(PlatformAuditLog.actor_name == "Scrub Test")
                .one()
            )
            assert row.new_data == {"name": "safe"}
            assert "password" not in (row.new_data or {})
