"""Hotel billing settings API tests."""

from tests.conftest import login


def test_owner_can_update_billing_settings(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    response = client.put(
        "/api/v1/tenants/me/billing-settings",
        headers=owner,
        json={"paper_size": "58mm"},
    )
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert data["paper_size"] == "58mm"
    assert data["width_mm"] == 58

    read = client.get("/api/v1/tenants/me/billing-settings", headers=owner)
    assert read.status_code == 200
    assert read.get_json()["data"]["paper_size"] == "58mm"


def test_billing_user_can_read_but_not_update_billing_settings(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    client.put(
        "/api/v1/tenants/me/billing-settings",
        headers=owner,
        json={"paper_size": "A4"},
    )

    read = client.get("/api/v1/tenants/me/billing-settings", headers=billing)
    assert read.status_code == 200
    assert read.get_json()["data"]["paper_size"] == "A4"

    denied = client.put(
        "/api/v1/tenants/me/billing-settings",
        headers=billing,
        json={"paper_size": "80mm"},
    )
    assert denied.status_code == 403


def test_custom_billing_settings_validation(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    bad = client.put(
        "/api/v1/tenants/me/billing-settings",
        headers=owner,
        json={"paper_size": "custom", "width_mm": 10},
    )
    assert bad.status_code == 400

    ok = client.put(
        "/api/v1/tenants/me/billing-settings",
        headers=owner,
        json={"paper_size": "custom", "width_mm": 90, "height_mm": 200},
    )
    assert ok.status_code == 200, ok.get_json()
    assert ok.get_json()["data"]["width_mm"] == 90
