"""Sprint BIZ-05 — supplier master."""

from tests.conftest import login


def test_create_and_list_suppliers(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    created = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={
            "name": "Fresh Foods Wholesale",
            "phone_country_code": "91",
            "phone": "9876601234",
            "gstin": "27AAAAA0000A1Z5",
            "email": "vendor@freshfoods.test",
            "address": "Market Yard, Pune",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["name"] == "Fresh Foods Wholesale"
    assert body["gstin"] == "27AAAAA0000A1Z5"
    assert body["is_active"] is True

    listing = client.get("/api/v1/suppliers?q=Fresh", headers=headers)
    assert listing.status_code == 200, listing.get_json()
    assert any(row["name"] == "Fresh Foods Wholesale" for row in listing.get_json()["data"])


def test_duplicate_phone_and_gstin_rejected(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    payload = {
        "name": "Supplier A",
        "phone_country_code": "91",
        "phone": "9876608888",
        "gstin": "27BBBBB0000B1Z5",
    }
    first = client.post("/api/v1/suppliers", headers=headers, json=payload)
    assert first.status_code == 201, first.get_json()

    dup_phone = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": "Supplier B", "phone_country_code": "91", "phone": "9876608888"},
    )
    assert dup_phone.status_code == 409, dup_phone.get_json()

    dup_gstin = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": "Supplier C", "gstin": "27BBBBB0000B1Z5"},
    )
    assert dup_gstin.status_code == 409, dup_gstin.get_json()


def test_supplier_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    created = client.post(
        "/api/v1/suppliers",
        headers=owner_a,
        json={"name": "Tenant A Supplier", "phone_country_code": "91", "phone": "9876611111"},
    )
    supplier_id = created.get_json()["data"]["id"]

    denied = client.get(f"/api/v1/suppliers/{supplier_id}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_deactivate_supplier_soft_delete(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    created = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": "Inactive Supplier", "phone_country_code": "91", "phone": "9876622222"},
    )
    supplier_id = created.get_json()["data"]["id"]

    deleted = client.delete(f"/api/v1/suppliers/{supplier_id}", headers=headers)
    assert deleted.status_code == 200, deleted.get_json()
    assert deleted.get_json()["data"]["is_active"] is False

    still_there = client.get(f"/api/v1/suppliers/{supplier_id}", headers=headers)
    assert still_there.status_code == 200, still_there.get_json()
    assert still_there.get_json()["data"]["is_active"] is False


def test_manager_can_manage_suppliers(client):
    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": "Manager Supplier", "phone_country_code": "91", "phone": "9876633333"},
    )
    assert response.status_code == 201, response.get_json()


def test_billing_user_read_only(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    created = client.post(
        "/api/v1/suppliers",
        headers=owner,
        json={"name": "Read Only Supplier", "phone_country_code": "91", "phone": "9876644444"},
    )
    supplier_id = created.get_json()["data"]["id"]

    billing = login(client, "billing@hotela.com", "Billing@12345")
    read_ok = client.get(f"/api/v1/suppliers/{supplier_id}", headers=billing)
    assert read_ok.status_code == 200, read_ok.get_json()

    write_denied = client.post(
        "/api/v1/suppliers",
        headers=billing,
        json={"name": "Blocked Supplier", "phone_country_code": "91", "phone": "9876655555"},
    )
    assert write_denied.status_code == 403, write_denied.get_json()
