"""Tenant isolation baseline tests."""

from tests.conftest import login


def test_owner_a_cannot_see_owner_b_users(client):
    headers_a = login(client, "owner@hotela.com", "Owner@12345")
    headers_b = login(client, "owner@hotelb.com", "Owner@12345")

    users_a = client.get("/api/v1/users", headers=headers_a).get_json()["data"]
    users_b = client.get("/api/v1/users", headers=headers_b).get_json()["data"]

    assert all(u["email"].endswith("@hotela.com") or u["email"] == "owner@hotela.com" for u in users_a)
    # Tenant B seeded with owner only in tests
    assert all(u["email"].endswith("@hotelb.com") for u in users_b)
    assert "owner@hotelb.com" not in {u["email"] for u in users_a}


def test_owner_a_cannot_get_user_from_tenant_b(client):
    headers_a = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get(
        "/api/v1/users/b1111111-1111-1111-1111-111111111111",
        headers=headers_a,
    )
    assert response.status_code == 404


def test_forged_tenant_id_in_body_ignored_on_user_create(client):
    headers_a = login(client, "owner@hotela.com", "Owner@12345")
    response = client.post(
        "/api/v1/users",
        headers=headers_a,
        json={
            "name": "Forged",
            "email": "forged@hotela.com",
            "password": "Billing@12345",
            "tenant_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        },
    )
    assert response.status_code == 201

    headers_b = login(client, "owner@hotelb.com", "Owner@12345")
    users_b = client.get("/api/v1/users", headers=headers_b).get_json()["data"]
    assert "forged@hotela.com" not in {u["email"] for u in users_b}


def test_tenant_profile_is_scoped(client):
    headers_a = login(client, "owner@hotela.com", "Owner@12345")
    headers_b = login(client, "owner@hotelb.com", "Owner@12345")

    tenant_a = client.get("/api/v1/tenants/me", headers=headers_a).get_json()["data"]
    tenant_b = client.get("/api/v1/tenants/me", headers=headers_b).get_json()["data"]

    assert tenant_a["business_name"] == "Hotel A"
    assert tenant_b["business_name"] == "Hotel B"
    assert tenant_a["business_type"] == "hotel_restaurant"
    assert tenant_b["business_type"] == "cafe_tea"
    assert tenant_a["id"] != tenant_b["id"]


def test_business_types_endpoint_is_public(client):
    response = client.get("/api/v1/tenants/business-types")
    assert response.status_code == 200
    types = response.get_json()["data"]["business_types"]
    codes = {row["code"] for row in types}
    assert "hotel_restaurant" in codes
    assert "clothing" in codes
    assert "travel_agency" in codes
    assert len(types) == 13
    assert "medical" not in codes
    assert "medical_store" not in codes
    assert "other" not in codes


def test_owner_can_update_business_type(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert data["business_type"] == "clothing"
    assert data["business_type_label"] == "Clothing Shops"
    assert data["fssai_relevant"] is False


def test_invalid_business_type_rejected(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "spaceship"},
    )
    assert response.status_code == 400


def test_billing_user_cannot_update_tenant(client):
    headers = login(client, "billing@hotela.com", "Billing@12345")
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_name": "Hacked Name"},
    )
    assert response.status_code == 403
