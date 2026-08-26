"""Sprint BIZ-65 — permission matrix + audit completeness."""

from app.constants.permissions import (
    INDUSTRY_PERMISSION_MATRIX,
    PERM_ITEMS_WRITE,
    has_permission,
)
from app.models.role import ROLE_MANAGER
from app.services.audit_service import AuditService
from app.utils.audit_scrub import scrub_audit_payload
from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def test_audit_scrub_redacts_secrets_and_document_numbers():
    cleaned = scrub_audit_payload(
        {
            "password": "secret",
            "document_number": "A1234567",
            "name": "Meera",
            "nested": {"access_token": "tok", "title": "Hotel"},
        }
    )
    assert "password" not in cleaned
    assert cleaned["document_number"] == "[REDACTED]"
    assert cleaned["name"] == "Meera"
    assert "access_token" not in cleaned["nested"]
    assert cleaned["nested"]["title"] == "Hotel"


def test_audit_service_persists_scrubbed_payload(app):
    with app.app_context():
        row = AuditService.log(
            tenant_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            action="CREATE_TRAVEL_BOOKING_DOCUMENT",
            entity_type="TRAVEL_BOOKING_DOCUMENT",
            entity_id="doc-1",
            new_data={"document_type": "PASSPORT", "document_number": "P999", "password": "x"},
            commit=True,
        )
        assert row.new_data["document_number"] == "[REDACTED]"
        assert "password" not in row.new_data
        assert row.new_data["document_type"] == "PASSPORT"


def test_audit_meta_and_module_filter(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")

    meta = client.get("/api/v1/audit-logs/meta", headers=owner)
    assert meta.status_code == 200, meta.get_json()
    data = meta.get_json()["data"]
    keys = {m["key"] for m in data["modules"]}
    assert "travel" in keys
    assert "wholesale" in keys
    assert "CREATE_TOUR_PACKAGE" in data["industry_actions"]

    pkg = client.post(
        "/api/v1/travel/packages",
        headers=owner,
        json={
            "code": "AUD65",
            "name": "Audit Package",
            "destination": "Goa",
            "duration_days": 2,
            "base_price": "4000",
            "gst_percentage": "0",
        },
    )
    assert pkg.status_code == 201, pkg.get_json()
    pkg_id = pkg.get_json()["data"]["id"]

    filtered = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"module": "travel", "per_page": 50},
    )
    assert filtered.status_code == 200
    types = {row["entity_type"] for row in filtered.get_json()["data"]}
    assert "TOUR_PACKAGE" in types
    assert all(
        t
        in {
            "TOUR_PACKAGE",
            "TRAVEL_BOOKING",
            "TRAVEL_AGENT",
            "TRAVEL_COMMISSION_ENTRY",
            "TRAVEL_ITINERARY_ITEM",
            "TRAVEL_BOOKING_DOCUMENT",
        }
        for t in types
    )

    updated = client.patch(
        f"/api/v1/travel/packages/{pkg_id}",
        headers=owner,
        json={"name": "Audit Package v2"},
    )
    assert updated.status_code == 200, updated.get_json()

    detail_list = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "UPDATE_TOUR_PACKAGE", "per_page": 10},
    )
    assert detail_list.status_code == 200
    rows = detail_list.get_json()["data"]
    assert rows
    detail = client.get(f"/api/v1/audit-logs/{rows[0]['id']}", headers=owner)
    assert detail.status_code == 200
    body = detail.get_json()["data"]
    assert body["old_data"] is not None
    assert body["new_data"]["name"] == "Audit Package v2"

    billing = login(client, "billing@hotela.com", "Billing@12345")
    assert client.get("/api/v1/audit-logs/meta", headers=billing).status_code == 403


def test_delete_price_list_leaves_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    created = client.post(
        "/api/v1/price-lists",
        headers=owner,
        json={"name": "Temp Delete List", "list_type": "WHOLESALE"},
    )
    assert created.status_code == 201, created.get_json()
    pl_id = created.get_json()["data"]["id"]

    deleted = client.delete(f"/api/v1/price-lists/{pl_id}", headers=owner)
    assert deleted.status_code == 200, deleted.get_json()
    assert client.get(f"/api/v1/price-lists/{pl_id}", headers=owner).status_code == 404

    logs = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={"action": "DELETE_PRICE_LIST", "entity_id": pl_id, "per_page": 10},
    )
    assert logs.status_code == 200
    rows = logs.get_json()["data"]
    assert len(rows) >= 1
    assert rows[0]["entity_id"] == pl_id

    detail = client.get(f"/api/v1/audit-logs/{rows[0]['id']}", headers=owner)
    assert detail.status_code == 200
    assert detail.get_json()["data"]["old_data"]["name"] == "Temp Delete List"


def test_delete_itinerary_leaves_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "travel_agency")
    pkg = client.post(
        "/api/v1/travel/packages",
        headers=owner,
        json={
            "code": "DEL65",
            "name": "Delete Itinerary Pack",
            "destination": "Pune",
            "duration_days": 2,
            "base_price": "2000",
            "gst_percentage": "0",
        },
    ).get_json()["data"]
    booking = client.post(
        "/api/v1/travel/bookings",
        headers=owner,
        json={"package_id": pkg["id"], "customer_name": "Iso", "pax_count": 1},
    ).get_json()["data"]
    item = client.post(
        f"/api/v1/travel/bookings/{booking['id']}/itinerary",
        headers=owner,
        json={"item_type": "ACTIVITY", "title": "Will Delete"},
    ).get_json()["data"]
    item_id = item["id"]

    assert (
        client.delete(
            f"/api/v1/travel/bookings/{booking['id']}/itinerary/{item_id}",
            headers=owner,
        ).status_code
        == 200
    )

    logs = client.get(
        "/api/v1/audit-logs",
        headers=owner,
        query_string={
            "action": "DELETE_TRAVEL_ITINERARY_ITEM",
            "entity_id": item_id,
            "per_page": 10,
        },
    )
    assert logs.status_code == 200
    assert any(row["entity_id"] == item_id for row in logs.get_json()["data"])


def test_industry_permission_matrix_documents_mappings():
    assert "repair_service" in INDUSTRY_PERMISSION_MATRIX
    assert INDUSTRY_PERMISSION_MATRIX["tour_packages"]["write"] == PERM_ITEMS_WRITE
    # Manager remains without items.write (BIZ-03); Owner-only for price lists / packages.
    assert not has_permission(ROLE_MANAGER, PERM_ITEMS_WRITE)
