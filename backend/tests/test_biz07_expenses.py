"""Sprint BIZ-07 — expenses module."""

from tests.conftest import login


def _create_expense(client, headers, **overrides):
    payload = {
        "category": "Utilities",
        "amount": "1500.00",
        "expense_date": "2026-08-01",
        "notes": "Electricity bill",
    }
    payload.update(overrides)
    response = client.post("/api/v1/expenses", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_create_and_list_expenses(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    created = _create_expense(client, headers)
    assert created["category"] == "Utilities"
    assert created["amount"] == 1500.0
    assert created["expense_date"] == "2026-08-01"

    listing = client.get("/api/v1/expenses?q=Electricity", headers=headers)
    assert listing.status_code == 200, listing.get_json()
    assert any(row["id"] == created["id"] for row in listing.get_json()["data"])


def test_date_filters(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _create_expense(client, headers, expense_date="2026-08-01", amount="100")
    _create_expense(client, headers, expense_date="2026-08-15", amount="200", category="Rent")
    _create_expense(client, headers, expense_date="2026-09-01", amount="300")

    in_range = client.get(
        "/api/v1/expenses",
        headers=headers,
        query_string={"from": "2026-08-01", "to": "2026-08-31"},
    )
    assert in_range.status_code == 200, in_range.get_json()
    rows = in_range.get_json()["data"]
    assert len(rows) == 2
    assert all("2026-08" in row["expense_date"] for row in rows)

    by_category = client.get(
        "/api/v1/expenses",
        headers=headers,
        query_string={"category": "Rent"},
    )
    assert by_category.status_code == 200, by_category.get_json()
    assert all(row["category"] == "Rent" for row in by_category.get_json()["data"])


def test_expense_summary(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _create_expense(client, headers, category="Utilities", amount="100", expense_date="2026-08-05")
    _create_expense(client, headers, category="Utilities", amount="250", expense_date="2026-08-10")
    _create_expense(client, headers, category="Rent", amount="5000", expense_date="2026-08-01")

    summary = client.get(
        "/api/v1/expenses/summary",
        headers=headers,
        query_string={"from": "2026-08-01", "to": "2026-08-31"},
    )
    assert summary.status_code == 200, summary.get_json()
    body = summary.get_json()["data"]
    assert body["total"] == 5350.0
    categories = {row["category"]: row["total"] for row in body["by_category"]}
    assert categories["Utilities"] == 350.0
    assert categories["Rent"] == 5000.0


def test_update_and_delete_expense(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    created = _create_expense(client, headers)

    updated = client.patch(
        f"/api/v1/expenses/{created['id']}",
        headers=headers,
        json={"amount": "1750", "notes": "Updated bill"},
    )
    assert updated.status_code == 200, updated.get_json()
    body = updated.get_json()["data"]
    assert body["amount"] == 1750.0
    assert body["notes"] == "Updated bill"

    deleted = client.delete(f"/api/v1/expenses/{created['id']}", headers=headers)
    assert deleted.status_code == 200, deleted.get_json()

    missing = client.get(f"/api/v1/expenses/{created['id']}", headers=headers)
    assert missing.status_code == 404, missing.get_json()


def test_expense_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    created = _create_expense(client, owner_a)

    denied = client.get(f"/api/v1/expenses/{created['id']}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_manager_can_manage_expenses(client):
    manager = login(client, "manager@hotela.com", "Manager@12345")
    created = _create_expense(client, manager, category="Transport", amount="450")
    assert created["category"] == "Transport"

    listing = client.get("/api/v1/expenses", headers=manager)
    assert listing.status_code == 200, listing.get_json()


def test_billing_user_denied_expenses(client):
    billing = login(client, "billing@hotela.com", "Billing@12345")
    denied = client.get("/api/v1/expenses", headers=billing)
    assert denied.status_code == 403, denied.get_json()

    write_denied = client.post(
        "/api/v1/expenses",
        headers=billing,
        json={"amount": "100", "expense_date": "2026-08-01"},
    )
    assert write_denied.status_code == 403, write_denied.get_json()
