"""Sprint 7: Master business list pagination + batched subscription loads."""

from tests.conftest import login, login_master
from tests.test_p8_4_trial_management import _approve


def test_business_list_paginates_without_500_cap(client, app):
    master = login_master(client, app)
    _approve(client, app, email="page-three@shop.test")

    first = client.get("/api/v1/master/businesses?page=1&per_page=1", headers=master)
    assert first.status_code == 200, first.get_json()
    meta = first.get_json()["meta"]
    assert meta["per_page"] == 1
    assert meta["page"] == 1
    assert meta["total"] >= 3
    assert len(first.get_json()["data"]) == 1
    first_id = first.get_json()["data"][0]["id"]

    second = client.get("/api/v1/master/businesses?page=2&per_page=1", headers=master)
    assert second.status_code == 200
    assert len(second.get_json()["data"]) == 1
    assert second.get_json()["data"][0]["id"] != first_id

    all_rows = client.get("/api/v1/master/businesses?per_page=100", headers=master)
    assert all_rows.status_code == 200
    assert all_rows.get_json()["meta"]["total"] >= 3
    names = {row["business_name"] for row in all_rows.get_json()["data"]}
    assert "Hotel A" in names
    assert "Hotel B" in names
    assert "Trial Shop" in names


def test_trials_list_paginates(client, app):
    master = login_master(client, app)
    _approve(client, app, email="trial-page-a@shop.test")
    _approve(client, app, email="trial-page-b@shop.test")

    first = client.get("/api/v1/master/trials?page=1&per_page=1", headers=master)
    assert first.status_code == 200, first.get_json()
    assert first.get_json()["meta"]["per_page"] == 1
    assert first.get_json()["meta"]["total"] >= 2
    assert len(first.get_json()["data"]) == 1

    second = client.get("/api/v1/master/trials?page=2&per_page=1", headers=master)
    assert second.status_code == 200
    assert len(second.get_json()["data"]) == 1
    assert second.get_json()["data"][0]["id"] != first.get_json()["data"][0]["id"]


def test_dashboard_counts_use_current_subscriptions(client, app):
    master = login_master(client, app)
    summary = client.get("/api/v1/master/dashboard/summary", headers=master)
    assert summary.status_code == 200, summary.get_json()
    data = summary.get_json()["data"]
    assert data["total_businesses"] >= 2
    assert "expiring_soon" in data
    assert "expired_subscriptions" in data


def test_owner_still_cannot_list_master_businesses(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert client.get("/api/v1/master/businesses?per_page=1", headers=owner).status_code == 403
