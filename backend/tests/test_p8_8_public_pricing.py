"""P8-8: public landing pricing from active public plans."""

from tests.conftest import login_master
from tests.test_p8_5_plan_management import _create_plan


def test_public_plans_are_anonymous_and_sorted(client, app):
    master = login_master(client, app)
    hidden = _create_plan(
        client,
        master,
        name="Hidden Plan",
        price=999,
        is_public=False,
        display_order=1,
    )
    yearly = _create_plan(
        client,
        master,
        name="Yearly Plan",
        price=4999,
        billing_cycle="YEARLY",
        display_order=20,
    )
    monthly = _create_plan(
        client,
        master,
        name="Monthly Plan",
        price=550,
        display_order=5,
    )
    inactive = _create_plan(
        client,
        master,
        name="Inactive Plan",
        price=400,
        is_active=False,
        display_order=2,
    )
    assert hidden.status_code == 201
    assert yearly.status_code == 201
    assert monthly.status_code == 201
    assert inactive.status_code == 201

    response = client.get("/api/v1/public/plans")

    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert [row["name"] for row in data] == ["Monthly Plan", "Yearly Plan"]
    assert data[0]["price"] == 550.0
    assert data[0]["billing_cycle"] == "MONTHLY"
    assert "subscriber_count" not in data[0]


def test_public_plans_do_not_require_business_or_master_auth(client):
    response = client.get("/api/v1/public/plans")
    assert response.status_code == 200, response.get_json()
