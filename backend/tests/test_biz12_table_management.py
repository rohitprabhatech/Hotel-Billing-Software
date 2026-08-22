"""Sprint BIZ-12 — shared table management module."""

from tests.conftest import login


def _create_table(client, headers, code, **extra):
    payload = {"code": code, **extra}
    response = client.post("/api/v1/tables", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_create_and_list_tables(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    created = _create_table(client, headers, "T1", section="Ground", capacity=4)
    assert created["code"] == "T1"
    assert created["status"] == "available"
    assert created["section"] == "Ground"
    assert created["capacity"] == 4

    listing = client.get("/api/v1/tables", headers=headers)
    assert listing.status_code == 200, listing.get_json()
    assert any(row["code"] == "T1" for row in listing.get_json()["data"])


def test_cafe_tenant_can_use_tables_module(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    response = client.get("/api/v1/tenants/me/modules", headers=headers)
    assert "table_management" in response.get_json()["data"]["enabled_modules"]
    created = _create_table(client, headers, "C1")
    assert created["code"] == "C1"


def test_table_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    table = _create_table(client, owner_a, "Iso-T1")

    denied = client.get(f"/api/v1/tables/{table['id']}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_status_transitions(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    table = _create_table(client, headers, "Status-T1")

    occupied = client.post(
        f"/api/v1/tables/{table['id']}/status",
        headers=headers,
        json={"status": "occupied"},
    )
    assert occupied.status_code == 200, occupied.get_json()
    assert occupied.get_json()["data"]["status"] == "occupied"

    invalid = client.post(
        f"/api/v1/tables/{table['id']}/status",
        headers=headers,
        json={"status": "reserved"},
    )
    assert invalid.status_code == 400, invalid.get_json()

    cleared = client.post(
        f"/api/v1/tables/{table['id']}/status",
        headers=headers,
        json={"status": "available"},
    )
    assert cleared.status_code == 200, cleared.get_json()


def test_billing_user_can_update_status_not_create(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    table = _create_table(client, owner, "Billing-T1")

    denied = client.post("/api/v1/tables", headers=billing, json={"code": "Billing-T2"})
    assert denied.status_code == 403, denied.get_json()

    allowed = client.post(
        f"/api/v1/tables/{table['id']}/status",
        headers=billing,
        json={"status": "occupied"},
    )
    assert allowed.status_code == 200, allowed.get_json()


def test_merge_and_unmerge_tables(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    primary = _create_table(client, headers, "Merge-P1", capacity=4)
    secondary = _create_table(client, headers, "Merge-S1", capacity=2)

    merged = client.post(
        "/api/v1/tables/merge",
        headers=headers,
        json={
            "primary_table_id": primary["id"],
            "secondary_table_ids": [secondary["id"]],
        },
    )
    assert merged.status_code == 200, merged.get_json()
    body = merged.get_json()["data"]
    assert body["status"] == "occupied"
    assert len(body["merged_tables"]) == 1
    assert body["merged_tables"][0]["code"] == "Merge-S1"

    unmerged = client.post(
        "/api/v1/tables/unmerge",
        headers=headers,
        json={"primary_table_id": primary["id"]},
    )
    assert unmerged.status_code == 200, unmerged.get_json()
    assert unmerged.get_json()["data"]["status"] == "available"
    assert unmerged.get_json()["data"]["merged_tables"] == []


def test_merge_requires_available_secondaries(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    primary = _create_table(client, headers, "Merge-P2")
    secondary = _create_table(client, headers, "Merge-S2")
    client.post(
        f"/api/v1/tables/{secondary['id']}/status",
        headers=headers,
        json={"status": "occupied"},
    )

    response = client.post(
        "/api/v1/tables/merge",
        headers=headers,
        json={
            "primary_table_id": primary["id"],
            "secondary_table_ids": [secondary["id"]],
        },
    )
    assert response.status_code == 400, response.get_json()


def test_tables_api_forbidden_without_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    response = client.get("/api/v1/tables", headers=headers)
    assert response.status_code == 403, response.get_json()


def test_table_status_change_is_audited(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    table = _create_table(client, headers, "Audit-T1")
    client.post(
        f"/api/v1/tables/{table['id']}/status",
        headers=headers,
        json={"status": "reserved"},
    )
    logs = client.get(
        "/api/v1/audit-logs",
        headers=headers,
        query_string={"action": "DINING_TABLE_STATUS_CHANGED", "per_page": 10},
    ).get_json()["data"]
    assert any(row["entity_id"] == table["id"] for row in logs)
