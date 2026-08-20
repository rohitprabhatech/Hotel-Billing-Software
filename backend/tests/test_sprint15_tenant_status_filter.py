"""Sprint 15: Master tenant_status filter on the businesses list."""

from tests.conftest import login, login_master
from tests.test_p8_4_trial_management import _approve


def test_tenant_status_filter_paginates_deactivated(client, app):
    first, master = _approve(client, app, email="acct-page-a@shop.test")
    second, _ = _approve(client, app, email="acct-page-b@shop.test")
    a_id = first.get_json()["data"]["tenant_id"]
    b_id = second.get_json()["data"]["tenant_id"]

    assert client.post(f"/api/v1/master/businesses/{a_id}/deactivate", headers=master).status_code == 200
    assert client.post(f"/api/v1/master/businesses/{b_id}/deactivate", headers=master).status_code == 200

    page1 = client.get(
        "/api/v1/master/businesses?tenant_status=SUSPENDED&page=1&per_page=1",
        headers=master,
    )
    assert page1.status_code == 200, page1.get_json()
    assert page1.get_json()["meta"]["per_page"] == 1
    assert page1.get_json()["meta"]["total"] >= 2
    assert len(page1.get_json()["data"]) == 1
    assert page1.get_json()["data"][0]["tenant_status"] == "SUSPENDED"
    first_id = page1.get_json()["data"][0]["id"]
    assert first_id in {a_id, b_id}

    page2 = client.get(
        "/api/v1/master/businesses?tenant_status=SUSPENDED&page=2&per_page=1",
        headers=master,
    )
    assert page2.status_code == 200
    assert len(page2.get_json()["data"]) == 1
    assert page2.get_json()["data"][0]["id"] != first_id
    assert page2.get_json()["data"][0]["id"] in {a_id, b_id}
    assert page2.get_json()["data"][0]["tenant_status"] == "SUSPENDED"

    active = client.get(
        "/api/v1/master/businesses?tenant_status=ACTIVE&per_page=100",
        headers=master,
    )
    ids = {row["id"] for row in active.get_json()["data"]}
    assert a_id not in ids
    assert b_id not in ids
    assert all(row["tenant_status"] == "ACTIVE" for row in active.get_json()["data"])


def test_tenant_status_combines_with_subscription_status(client, app):
    approved, master = _approve(client, app, email="acct-trial@shop.test")
    tenant_id = approved.get_json()["data"]["tenant_id"]

    listed = client.get(
        "/api/v1/master/businesses?tenant_status=ACTIVE&status=TRIAL&per_page=100",
        headers=master,
    )
    assert listed.status_code == 200, listed.get_json()
    ids = {row["id"] for row in listed.get_json()["data"]}
    assert tenant_id in ids
    assert all(row["tenant_status"] == "ACTIVE" for row in listed.get_json()["data"])
    assert all(row["subscription"]["status"] == "TRIAL" for row in listed.get_json()["data"])


def test_invalid_tenant_status_rejected(client, app):
    master = login_master(client, app)
    bad = client.get("/api/v1/master/businesses?tenant_status=DEACTIVATED", headers=master)
    assert bad.status_code == 400


def test_owner_cannot_filter_tenant_status(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert (
        client.get(
            "/api/v1/master/businesses?tenant_status=SUSPENDED",
            headers=owner,
        ).status_code
        == 403
    )
