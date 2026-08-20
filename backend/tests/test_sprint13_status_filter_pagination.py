"""Sprint 13: status-filtered Master business list paginates without a 500 cap."""

from tests.conftest import login, login_master
from tests.test_p8_4_trial_management import _approve


def test_trial_status_filter_paginates(client, app):
    master = login_master(client, app)
    _approve(client, app, email="status-page-a@shop.test")
    _approve(client, app, email="status-page-b@shop.test")

    first = client.get(
        "/api/v1/master/businesses?status=TRIAL&page=1&per_page=1",
        headers=master,
    )
    assert first.status_code == 200, first.get_json()
    assert first.get_json()["meta"]["per_page"] == 1
    assert first.get_json()["meta"]["total"] >= 2
    assert len(first.get_json()["data"]) == 1
    assert first.get_json()["data"][0]["subscription"]["status"] == "TRIAL"
    first_id = first.get_json()["data"][0]["id"]

    second = client.get(
        "/api/v1/master/businesses?status=TRIAL&page=2&per_page=1",
        headers=master,
    )
    assert second.status_code == 200
    assert len(second.get_json()["data"]) == 1
    assert second.get_json()["data"][0]["id"] != first_id
    assert second.get_json()["data"][0]["subscription"]["status"] == "TRIAL"


def test_active_status_filter_includes_seed_hotels(client, app):
    master = login_master(client, app)
    listed = client.get(
        "/api/v1/master/businesses?status=ACTIVE&per_page=100",
        headers=master,
    )
    assert listed.status_code == 200, listed.get_json()
    names = {row["business_name"] for row in listed.get_json()["data"]}
    assert "Hotel A" in names
    assert "Hotel B" in names
    assert all(row["subscription"]["status"] == "ACTIVE" for row in listed.get_json()["data"])


def test_owner_cannot_filter_master_businesses(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert (
        client.get(
            "/api/v1/master/businesses?status=TRIAL&per_page=1",
            headers=owner,
        ).status_code
        == 403
    )
