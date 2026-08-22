"""Sprint BIZ-02 — module configuration framework."""

from app.constants.business_types import ALLOWED_BUSINESS_TYPES
from app.constants.modules import CORE_MODULES, defaults_for_business_type, list_module_catalog
from tests.conftest import login


def test_defaults_cover_all_fourteen_types():
    for code in ALLOWED_BUSINESS_TYPES:
        enabled = defaults_for_business_type(code)
        assert CORE_MODULES <= enabled
        assert len(enabled) >= len(CORE_MODULES)


def test_restaurant_has_tables_clothing_does_not():
    restaurant = defaults_for_business_type("hotel_restaurant")
    clothing = defaults_for_business_type("clothing")
    assert "restaurant_menu" in restaurant
    assert "table_management" in restaurant
    assert "kot" in restaurant
    assert "table_management" not in clothing
    assert "variants" in clothing
    assert "variants" not in restaurant


def test_catalog_lists_modules():
    rows = list_module_catalog()
    assert any(r["code"] == "table_management" for r in rows)
    assert any(r["is_core"] for r in rows)


def test_me_modules_endpoint(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert response.status_code == 200, response.get_json()
    data = response.get_json()["data"]
    assert data["business_type"] == "hotel_restaurant"
    assert "restaurant_menu" in data["enabled_modules"]
    assert "table_management" in data["enabled_modules"]
    assert "variants" not in data["enabled_modules"]
    assert any(m["code"] == "table_management" and m["enabled"] for m in data["modules"])
    assert any(m["code"] == "variants" and not m["enabled"] for m in data["modules"])


def test_tables_api_allowed_for_restaurant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/tables", headers=headers)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_tables_api_forbidden_for_clothing_tenant(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    response = client.get("/api/v1/tables", headers=headers)
    assert response.status_code == 403, response.get_json()
    body = response.get_json()
    assert body["error"]["code"] == "FORBIDDEN"

    variants = client.get("/api/v1/item-variants", headers=headers)
    assert variants.status_code == 200, variants.get_json()


def test_tenant_me_includes_enabled_modules(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me", headers=headers)
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert "enabled_modules" in data
    assert "core_billing" in data["enabled_modules"]
