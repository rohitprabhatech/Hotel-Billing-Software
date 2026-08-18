"""P8-4: configurable trial ON/OFF + days; new approvals only."""

from app.extensions import db
from app.models.subscription import SUBSCRIPTION_TRIAL, Subscription
from app.services.platform_settings_service import PlatformSettingsService
from tests.conftest import login, login_master


def _register(client, email="trial-owner@shop.test"):
    return client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Trial Shop",
            "business_type": "retail_shop",
            "owner_name": "Trial Owner",
            "owner_email": email,
            "password": "Trial@12345",
            "confirm_password": "Trial@12345",
            "terms_accepted": True,
        },
    )


def _approve(client, app, email="trial-owner@shop.test"):
    created = _register(client, email=email)
    assert created.status_code == 201, created.get_json()
    request_id = created.get_json()["data"]["request_id"]
    master = login_master(client, app)
    approved = client.post(
        f"/api/v1/master/registration-requests/{request_id}/approve",
        headers=master,
    )
    assert approved.status_code == 200, approved.get_json()
    return approved, master


def test_default_trial_settings(client, app):
    master = login_master(client, app)
    response = client.get("/api/v1/master/settings/trial", headers=master)
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert data["trial_enabled"] is True
    assert data["trial_days"] == 15


def test_owner_cannot_read_or_update_trial_settings(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert client.get("/api/v1/master/settings/trial", headers=owner).status_code == 403
    assert (
        client.put(
            "/api/v1/master/settings/trial",
            headers=owner,
            json={"trial_enabled": False, "trial_days": 7},
        ).status_code
        == 403
    )


def test_reject_zero_or_invalid_trial_days(client, app):
    master = login_master(client, app)
    zero = client.put(
        "/api/v1/master/settings/trial",
        headers=master,
        json={"trial_enabled": True, "trial_days": 0},
    )
    assert zero.status_code == 400
    huge = client.put(
        "/api/v1/master/settings/trial",
        headers=master,
        json={"trial_enabled": True, "trial_days": 400},
    )
    assert huge.status_code == 400


def test_approve_starts_configured_trial(client, app):
    approved, master = _approve(client, app)
    sub = approved.get_json()["data"]["subscription"]
    assert sub["status"] == SUBSCRIPTION_TRIAL
    assert sub["remaining_days"] == 15

    headers = login(client, "trial-owner@shop.test", "Trial@12345")
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200, me_res.get_json()
    me = me_res.get_json()["data"]
    assert me["tenant"]["subscription"]["status"] == "TRIAL"
    assert me["tenant"]["subscription"]["remaining_days"] == 15

    summary = client.get("/api/v1/master/dashboard/summary", headers=master).get_json()["data"]
    assert summary["trial_businesses"] == 1

    listed = client.get("/api/v1/master/trials", headers=master)
    assert listed.status_code == 200
    assert any(row["tenant_id"] == me["tenant"]["id"] for row in listed.get_json()["data"])


def test_disabled_trial_does_not_create_subscription(client, app):
    master = login_master(client, app)
    updated = client.put(
        "/api/v1/master/settings/trial",
        headers=master,
        json={"trial_enabled": False, "trial_days": 15},
    )
    assert updated.status_code == 200
    assert updated.get_json()["data"]["trial_enabled"] is False

    approved, _ = _approve(client, app, email="no-trial@shop.test")
    assert approved.get_json()["data"]["subscription"] is None
    headers = login(client, "no-trial@shop.test", "Trial@12345")
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200, me_res.get_json()
    me = me_res.get_json()["data"]
    assert me["tenant"]["subscription"] is None


def test_changing_settings_does_not_alter_existing_trial(client, app):
    approved, master = _approve(client, app, email="keep-trial@shop.test")
    original_end = approved.get_json()["data"]["subscription"]["trial_ends_at"]
    original_id = approved.get_json()["data"]["subscription"]["id"]

    client.put(
        "/api/v1/master/settings/trial",
        headers=master,
        json={"trial_enabled": True, "trial_days": 7},
    )

    with app.app_context():
        row = db.session.get(Subscription, original_id)
        assert row is not None
        assert row.trial_ends_at.isoformat() == original_end
        assert PlatformSettingsService.get_or_create().trial_days == 7

    second, _ = _approve(client, app, email="seven-day@shop.test")
    assert second.get_json()["data"]["subscription"]["remaining_days"] == 7


def test_seeded_owner_has_complimentary_subscription(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    me = client.get("/api/v1/auth/me", headers=headers).get_json()["data"]
    sub = me["tenant"]["subscription"]
    assert sub is not None
    assert sub["status"] == "ACTIVE"
    assert sub["access_allowed"] is True
    assert sub["is_complimentary"] is True
