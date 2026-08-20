"""Sprint 14: Master registration request list pagination."""

from tests.conftest import login, login_master
from tests.test_p8_3_registration_approval import _register


def test_registration_requests_paginates(client, app):
    master = login_master(client, app)
    first = _register(client, owner_email="page-a@shop.test", business_name="Alpha Cafe")
    second = _register(client, owner_email="page-b@shop.test", business_name="Beta Mart")
    assert first.status_code == 201, first.get_json()
    assert second.status_code == 201, second.get_json()

    page1 = client.get(
        "/api/v1/master/registration-requests?status=PENDING&page=1&per_page=1",
        headers=master,
    )
    assert page1.status_code == 200, page1.get_json()
    assert page1.get_json()["meta"]["per_page"] == 1
    assert page1.get_json()["meta"]["total"] >= 2
    assert len(page1.get_json()["data"]) == 1
    first_id = page1.get_json()["data"][0]["id"]

    page2 = client.get(
        "/api/v1/master/registration-requests?status=PENDING&page=2&per_page=1",
        headers=master,
    )
    assert page2.status_code == 200
    assert len(page2.get_json()["data"]) == 1
    assert page2.get_json()["data"][0]["id"] != first_id


def test_owner_cannot_paginate_registration_requests(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    assert (
        client.get(
            "/api/v1/master/registration-requests?page=1&per_page=1",
            headers=owner,
        ).status_code
        == 403
    )
