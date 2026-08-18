"""P8-6: subscription lifecycle + tenant access gate."""

from datetime import timedelta

from app.extensions import db
from app.models.subscription import SUBSCRIPTION_ACTIVE, SUBSCRIPTION_EXPIRED, Subscription
from app.utils.tokens import utc_now_naive
from tests.conftest import login, login_master
from tests.test_p8_4_trial_management import _approve
from tests.test_p8_5_plan_management import _create_plan


def test_owner_cannot_manage_master_businesses(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert client.get("/api/v1/master/businesses", headers=owner).status_code == 403


def test_grandfathered_owner_can_list_bills(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/bills", headers=owner)
    assert response.status_code == 200, response.get_json()


def test_expired_trial_can_login_but_not_bill(client, app):
    approved, _ = _approve(client, app, email="expire-soon@shop.test")
    sub_id = approved.get_json()["data"]["subscription"]["id"]
    with app.app_context():
        row = db.session.get(Subscription, sub_id)
        row.trial_ends_at = utc_now_naive() - timedelta(days=1)
        row.ends_at = row.trial_ends_at
        db.session.commit()

    headers = login(client, "expire-soon@shop.test", "Trial@12345")
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200, me.get_json()
    assert me.get_json()["data"]["tenant"]["subscription"]["status"] == SUBSCRIPTION_EXPIRED
    assert me.get_json()["data"]["tenant"]["subscription"]["access_allowed"] is False

    blocked = client.get("/api/v1/bills", headers=headers)
    assert blocked.status_code == 402
    assert blocked.get_json()["error"]["code"] == "SUBSCRIPTION_INACTIVE"

    profile = client.get("/api/v1/profile", headers=headers)
    assert profile.status_code == 200


def test_trial_off_approve_is_gated_until_assign(client, app):
    master = login_master(client, app)
    client.put(
        "/api/v1/master/settings/trial",
        headers=master,
        json={"trial_enabled": False, "trial_days": 15},
    )
    approved, master = _approve(client, app, email="no-trial-gate@shop.test")
    assert approved.get_json()["data"]["subscription"] is None

    owner = login(client, "no-trial-gate@shop.test", "Trial@12345")
    assert client.get("/api/v1/bills", headers=owner).status_code == 402

    plan = _create_plan(client, master, name="Access Plan", price=550)
    plan_id = plan.get_json()["data"]["id"]
    tenant_id = owner and client.get("/api/v1/auth/me", headers=owner).get_json()["data"]["tenant"]["id"]

    granted = client.post(
        f"/api/v1/master/businesses/{tenant_id}/assign-plan",
        headers=master,
        json={"plan_id": plan_id},
    )
    assert granted.status_code == 200, granted.get_json()
    assert granted.get_json()["data"]["access_allowed"] is True
    assert client.get("/api/v1/bills", headers=owner).status_code == 200


def test_inactive_plan_cannot_be_assigned(client, app):
    master = login_master(client, app)
    created = _create_plan(client, master, name="Retired Plan", price=100)
    plan_id = created.get_json()["data"]["id"]
    client.patch(
        f"/api/v1/master/plans/{plan_id}/status",
        headers=master,
        json={"is_active": False},
    )
    listed = client.get("/api/v1/master/businesses", headers=master)
    tenant_id = listed.get_json()["data"][0]["id"]
    denied = client.post(
        f"/api/v1/master/businesses/{tenant_id}/assign-plan",
        headers=master,
        json={"plan_id": plan_id},
    )
    assert denied.status_code == 400


def test_renew_snapshots_price_and_does_not_follow_later_plan_change(client, app):
    master = login_master(client, app)
    created = _create_plan(client, master, name="Renew Plan", price=550)
    plan_id = created.get_json()["data"]["id"]
    tenant_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    renewed = client.post(
        f"/api/v1/master/businesses/{tenant_id}/renew",
        headers=master,
        json={"days": 30, "plan_id": plan_id},
    )
    assert renewed.status_code == 200, renewed.get_json()
    assert renewed.get_json()["data"]["price_at_purchase"] == 550.0
    assert renewed.get_json()["data"]["status"] == SUBSCRIPTION_ACTIVE
    original = renewed.get_json()["data"]["price_at_purchase"]

    client.put(
        f"/api/v1/master/plans/{plan_id}",
        headers=master,
        json={"price": 650},
    )
    detail = client.get(f"/api/v1/master/businesses/{tenant_id}", headers=master)
    assert detail.get_json()["data"]["subscription"]["price_at_purchase"] == original


def test_cancel_blocks_access(client, app):
    master = login_master(client, app)
    tenant_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    cancelled = client.post(
        f"/api/v1/master/businesses/{tenant_id}/cancel-subscription",
        headers=master,
    )
    assert cancelled.status_code == 200
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert client.get("/api/v1/bills", headers=owner).status_code == 402


def test_extend_trial_increases_remaining_days(client, app):
    approved, master = _approve(client, app, email="extend-me@shop.test")
    tenant_id = client.get(
        "/api/v1/auth/me",
        headers=login(client, "extend-me@shop.test", "Trial@12345"),
    ).get_json()["data"]["tenant"]["id"]
    before = approved.get_json()["data"]["subscription"]["remaining_days"]
    extended = client.post(
        f"/api/v1/master/businesses/{tenant_id}/extend-trial",
        headers=master,
        json={"days": 10},
    )
    assert extended.status_code == 200, extended.get_json()
    assert extended.get_json()["data"]["remaining_days"] == before + 10


def test_expiring_filter_uses_warning_window(client, app):
    approved, master = _approve(client, app, email="warn-me@shop.test")
    sub_id = approved.get_json()["data"]["subscription"]["id"]
    with app.app_context():
        row = db.session.get(Subscription, sub_id)
        row.trial_ends_at = utc_now_naive() + timedelta(days=3)
        row.ends_at = row.trial_ends_at
        db.session.commit()

    expiring = client.get("/api/v1/master/businesses/expiring", headers=master)
    assert expiring.status_code == 200, expiring.get_json()
    names = [row["business_name"] for row in expiring.get_json()["data"]]
    assert "Trial Shop" in names

    summary = client.get("/api/v1/master/dashboard/summary", headers=master).get_json()["data"]
    assert summary["expiring_soon"] >= 1
