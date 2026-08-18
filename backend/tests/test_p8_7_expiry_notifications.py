"""P8-7: expiry notifications, email, and scheduled checks."""

from datetime import timedelta

from app.extensions import db
from app.models.subscription import SUBSCRIPTION_ACTIVE, Subscription
from app.services.email_service import EmailService
from app.utils.tokens import utc_now_naive
from tests.conftest import login, login_master
from tests.test_p8_4_trial_management import _approve
from tests.test_p8_5_plan_management import _create_plan


def _set_subscription_window(app, subscription_id: str, *, days: int, status: str = SUBSCRIPTION_ACTIVE):
    with app.app_context():
        row = db.session.get(Subscription, subscription_id)
        row.status = status
        row.ends_at = utc_now_naive() + timedelta(days=days)
        if row.trial_ends_at is not None:
            row.trial_ends_at = row.ends_at
        db.session.commit()


def _set_complimentary(app, subscription_id: str):
    with app.app_context():
        row = db.session.get(Subscription, subscription_id)
        row.status = SUBSCRIPTION_ACTIVE
        row.ends_at = None
        row.trial_ends_at = None
        db.session.commit()


def test_expiry_job_is_idempotent_for_expiring_notice(client, app):
    EmailService.clear_outbox()
    owner_headers = login(client, "owner@hotela.com", "Owner@12345")
    me = client.get("/api/v1/auth/me", headers=owner_headers)
    sub_id = me.get_json()["data"]["tenant"]["subscription"]["id"]
    _set_subscription_window(app, sub_id, days=2)

    master = login_master(client, app)
    first = client.post("/api/v1/master/jobs/expiry-check", headers=master)
    second = client.post("/api/v1/master/jobs/expiry-check", headers=master)

    assert first.status_code == 200, first.get_json()
    assert first.get_json()["data"]["expiring_notices"] == 1
    assert second.status_code == 200, second.get_json()
    assert second.get_json()["data"]["expiring_notices"] == 0
    assert len(EmailService.get_outbox()) == 1

    notices = client.get("/api/v1/notifications", headers=owner_headers)
    assert notices.status_code == 200, notices.get_json()
    assert notices.get_json()["data"][0]["type"] == "SUBSCRIPTION_EXPIRING"


def test_complimentary_subscription_does_not_notify(client, app):
    EmailService.clear_outbox()
    owner_headers = login(client, "owner@hotela.com", "Owner@12345")
    me = client.get("/api/v1/auth/me", headers=owner_headers)
    sub_id = me.get_json()["data"]["tenant"]["subscription"]["id"]
    _set_complimentary(app, sub_id)

    master = login_master(client, app)
    response = client.post("/api/v1/master/jobs/expiry-check", headers=master)

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["data"]["expiring_notices"] == 0
    assert response.get_json()["data"]["expired_notices"] == 0
    assert EmailService.get_outbox() == []


def test_expired_subscription_sends_one_notice(client, app):
    EmailService.clear_outbox()
    approved, master = _approve(client, app, email="expired-one@shop.test")
    EmailService.clear_outbox()
    sub_id = approved.get_json()["data"]["subscription"]["id"]
    _set_subscription_window(app, sub_id, days=-1)

    response = client.post("/api/v1/master/jobs/expiry-check", headers=master)

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["data"]["expired_notices"] == 1
    assert len(EmailService.get_outbox()) == 1
    assert "has expired" in EmailService.get_outbox()[0]["subject"]


def test_owner_cannot_access_master_notifications_or_job(client, app):
    owner = login(client, "owner@hotela.com", "Owner@12345")

    assert client.get("/api/v1/master/notifications", headers=owner).status_code == 403
    assert client.get("/api/v1/master/notifications/unread-count", headers=owner).status_code == 403
    assert client.post("/api/v1/master/jobs/expiry-check", headers=owner).status_code == 403


def test_master_can_read_notifications_after_job(client, app):
    EmailService.clear_outbox()
    owner_headers = login(client, "owner@hotela.com", "Owner@12345")
    sub_id = client.get("/api/v1/auth/me", headers=owner_headers).get_json()["data"]["tenant"]["subscription"]["id"]
    _set_subscription_window(app, sub_id, days=1)

    master = login_master(client, app)
    run = client.post("/api/v1/master/jobs/expiry-check", headers=master)
    listed = client.get("/api/v1/master/notifications", headers=master)

    assert run.status_code == 200, run.get_json()
    assert listed.status_code == 200, listed.get_json()
    assert listed.get_json()["meta"]["unread_count"] >= 1
    assert listed.get_json()["data"][0]["type"] == "SUBSCRIPTION_EXPIRING"


def test_new_period_after_renew_can_notify_again(client, app):
    EmailService.clear_outbox()
    owner_headers = login(client, "owner@hotela.com", "Owner@12345")
    me = client.get("/api/v1/auth/me", headers=owner_headers)
    tenant_id = me.get_json()["data"]["tenant"]["id"]
    sub_id = me.get_json()["data"]["tenant"]["subscription"]["id"]
    _set_subscription_window(app, sub_id, days=2)

    master = login_master(client, app)
    first = client.post("/api/v1/master/jobs/expiry-check", headers=master)
    assert first.status_code == 200, first.get_json()
    assert first.get_json()["data"]["expiring_notices"] == 1

    plan = _create_plan(client, master, name="Renew Notify Plan", price=550)
    plan_id = plan.get_json()["data"]["id"]
    renewed = client.post(
        f"/api/v1/master/businesses/{tenant_id}/renew",
        headers=master,
        json={"days": 30, "plan_id": plan_id},
    )
    assert renewed.status_code == 200, renewed.get_json()

    _set_subscription_window(app, sub_id, days=1)
    second = client.post("/api/v1/master/jobs/expiry-check", headers=master)

    assert second.status_code == 200, second.get_json()
    assert second.get_json()["data"]["expiring_notices"] == 1
    assert len(EmailService.get_outbox()) == 2
