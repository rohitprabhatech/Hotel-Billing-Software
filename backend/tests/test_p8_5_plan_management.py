"""P8-5: Master Admin subscription plan catalog."""

from decimal import Decimal

from app.extensions import db
from app.models.subscription import SUBSCRIPTION_ACTIVE, Subscription
from app.utils.ids import new_uuid
from app.utils.tokens import utc_now_naive
from tests.conftest import login, login_master

TENANT_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


def _create_plan(client, headers, **overrides):
    payload = {
        "name": "Business Billing Plan",
        "description": "Monthly subscription",
        "price": 550,
        "billing_cycle": "MONTHLY",
        "trial_eligible": True,
        "is_public": True,
        "is_active": True,
        "display_order": 1,
        "features": ["Billing", "Reports"],
    }
    payload.update(overrides)
    return client.post("/api/v1/master/plans", headers=headers, json=payload)


def test_owner_cannot_manage_plans(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert client.get("/api/v1/master/plans", headers=owner).status_code == 403
    assert (
        client.post(
            "/api/v1/master/plans",
            headers=owner,
            json={"name": "Nope", "price": 100},
        ).status_code
        == 403
    )


def test_create_list_get_update_plan(client, app):
    master = login_master(client, app)
    created = _create_plan(client, master)
    assert created.status_code == 201, created.get_json()
    plan = created.get_json()["data"]
    assert plan["name"] == "Business Billing Plan"
    assert plan["price"] == 550.0
    assert plan["currency"] == "INR"
    assert plan["billing_cycle"] == "MONTHLY"
    assert plan["features"] == ["Billing", "Reports"]
    assert plan["subscriber_count"] == 0

    listed = client.get("/api/v1/master/plans", headers=master)
    assert listed.status_code == 200
    assert any(row["id"] == plan["id"] for row in listed.get_json()["data"])

    detail = client.get(f"/api/v1/master/plans/{plan['id']}", headers=master)
    assert detail.status_code == 200
    assert detail.get_json()["data"]["id"] == plan["id"]

    updated = client.put(
        f"/api/v1/master/plans/{plan['id']}",
        headers=master,
        json={"name": "Business Billing Plus", "display_order": 3},
    )
    assert updated.status_code == 200, updated.get_json()
    data = updated.get_json()["data"]
    assert data["name"] == "Business Billing Plus"
    assert data["price"] == 550.0
    assert data["display_order"] == 3


def test_reject_negative_price_and_empty_name(client, app):
    master = login_master(client, app)
    negative = _create_plan(client, master, name="Bad price", price=-1)
    assert negative.status_code == 400
    empty = _create_plan(client, master, name="  ", price=100)
    assert empty.status_code == 400


def test_list_sorted_by_display_order(client, app):
    master = login_master(client, app)
    later = _create_plan(client, master, name="Zebra Plan", display_order=20, price=800)
    earlier = _create_plan(client, master, name="Alpha Plan", display_order=5, price=400)
    assert later.status_code == 201
    assert earlier.status_code == 201

    listed = client.get("/api/v1/master/plans", headers=master)
    names = [row["name"] for row in listed.get_json()["data"]]
    assert names.index("Alpha Plan") < names.index("Zebra Plan")


def test_deactivate_keeps_existing_subscription(client, app):
    master = login_master(client, app)
    created = _create_plan(client, master, name="Keep subscribers")
    plan_id = created.get_json()["data"]["id"]

    with app.app_context():
        sub = Subscription(
            id=new_uuid(),
            tenant_id=TENANT_A,
            plan_id=plan_id,
            status=SUBSCRIPTION_ACTIVE,
            starts_at=utc_now_naive(),
            price_at_purchase=Decimal("550.00"),
        )
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

    deactivated = client.patch(
        f"/api/v1/master/plans/{plan_id}/status",
        headers=master,
        json={"is_active": False},
    )
    assert deactivated.status_code == 200, deactivated.get_json()
    assert deactivated.get_json()["data"]["is_active"] is False

    hidden = client.get("/api/v1/master/plans?include_inactive=false", headers=master)
    assert all(row["id"] != plan_id for row in hidden.get_json()["data"])

    with app.app_context():
        row = db.session.get(Subscription, sub_id)
        assert row is not None
        assert row.plan_id == plan_id
        assert row.status == SUBSCRIPTION_ACTIVE
        assert row.price_at_purchase == Decimal("550.00")


def test_price_change_does_not_rewrite_price_at_purchase(client, app):
    master = login_master(client, app)
    created = _create_plan(client, master, name="Snapshot price", price=550)
    plan_id = created.get_json()["data"]["id"]

    with app.app_context():
        sub = Subscription(
            id=new_uuid(),
            tenant_id=TENANT_A,
            plan_id=plan_id,
            status=SUBSCRIPTION_ACTIVE,
            starts_at=utc_now_naive(),
            price_at_purchase=Decimal("550.00"),
        )
        db.session.add(sub)
        db.session.commit()
        sub_id = sub.id

    changed = client.put(
        f"/api/v1/master/plans/{plan_id}",
        headers=master,
        json={"price": 650},
    )
    assert changed.status_code == 200, changed.get_json()
    assert changed.get_json()["data"]["price"] == 650.0

    with app.app_context():
        row = db.session.get(Subscription, sub_id)
        assert row.price_at_purchase == Decimal("550.00")
        assert row.plan_id == plan_id
