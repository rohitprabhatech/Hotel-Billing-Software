"""Sprint BIZ-01 — 13 business types catalog (hardware + building material combined)."""

from app.constants.business_types import (
    ALLOWED_BUSINESS_TYPES,
    LEGACY_BUSINESS_TYPE_MAP,
    coerce_business_type,
    list_business_types,
    map_legacy_business_type,
    normalize_business_type,
)


def test_catalog_has_exactly_thirteen_types():
    rows = list_business_types()
    assert len(rows) == 13
    assert len(ALLOWED_BUSINESS_TYPES) == 13
    codes = {r["code"] for r in rows}
    assert codes == ALLOWED_BUSINESS_TYPES
    assert "other" not in codes
    assert "building_material" not in codes
    assert "medical" not in codes
    assert "medical_store" not in codes
    assert "pharmacy" not in codes


def test_normalize_accepts_canonical_only_by_default():
    assert normalize_business_type("hotel_restaurant") == "hotel_restaurant"
    try:
        normalize_business_type("hotel")
        assert False, "legacy hotel should be rejected on write"
    except ValueError:
        pass


def test_normalize_maps_legacy_when_allowed():
    assert normalize_business_type("hotel", allow_legacy=True) == "hotel_restaurant"
    assert normalize_business_type("kirana_store", allow_legacy=True) == "grocery_kirana"
    for legacy, canonical in LEGACY_BUSINESS_TYPE_MAP.items():
        assert normalize_business_type(legacy, allow_legacy=True) == canonical


def test_medical_codes_rejected():
    for code in ("medical", "medical_store", "pharmacy", "chemist"):
        try:
            normalize_business_type(code)
            assert False, code
        except ValueError as exc:
            assert "Medical" in str(exc) or "not supported" in str(exc).lower()


def test_coerce_and_map_helpers():
    assert map_legacy_business_type("clothing_store") == "clothing"
    assert coerce_business_type("electronics_store") == "electronics"
    assert coerce_business_type(None) == "grocery_kirana"
    assert coerce_business_type("") == "grocery_kirana"


def test_building_material_maps_to_hardware():
    assert map_legacy_business_type("building_material") == "hardware"
    assert coerce_business_type("building_material") == "hardware"
    assert normalize_business_type("building_material", allow_legacy=True) == "hardware"


def test_api_lists_thirteen_types(client):
    response = client.get("/api/v1/tenants/business-types")
    assert response.status_code == 200
    types = response.get_json()["data"]["business_types"]
    assert len(types) == 13
    codes = [t["code"] for t in types]
    assert codes[0] == "hotel_restaurant"
    assert "travel_agency" in codes
    assert all(t.get("label") for t in types)


def test_register_rejects_medical_and_legacy(client):
    for bad in ("medical_store", "pharmacy", "hotel", "other"):
        response = client.post(
            "/api/v1/auth/register-business",
            json={
                "business_name": f"Bad {bad}",
                "business_type": bad,
                "owner_name": "Owner",
                "owner_email": f"owner@{bad.replace('_', '')}.biz01.test",
                "password": "Biz01Test@123",
                "confirm_password": "Biz01Test@123",
                "terms_accepted": True,
            },
        )
        assert response.status_code == 400, bad


def test_register_accepts_canonical(client):
    response = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": "Travel Pro",
            "business_type": "travel_agency",
            "owner_name": "Travel Owner",
            "owner_email": "owner@travel.biz01.test",
            "password": "Biz01Test@123",
            "confirm_password": "Biz01Test@123",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["data"]["business_type"] == "travel_agency"


def test_owner_business_type_change_is_audited(client):
    from tests.conftest import login

    headers = login(client, "owner@hotela.com", "Owner@12345")
    before = client.get("/api/v1/tenants/me", headers=headers).get_json()["data"]
    assert before["business_type"] == "hotel_restaurant"

    updated = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "wholesale"},
    )
    assert updated.status_code == 200, updated.get_json()
    data = updated.get_json()["data"]
    assert data["business_type"] == "wholesale"
    assert data["business_type_label"] == "Wholesale Shops"

    audits = client.get("/api/v1/audit-logs", headers=headers)
    assert audits.status_code == 200
    payload = audits.get_json()["data"]
    rows = payload if isinstance(payload, list) else (
        payload.get("items") or payload.get("logs") or payload.get("results") or []
    )
    assert any(r.get("action") == "UPDATE_TENANT" for r in rows)
