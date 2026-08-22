"""Sprint BIZ-03 — Manager role and permission matrix."""

from app.constants.permissions import PERM_REPORTS, permissions_for_role
from app.models.role import ROLE_MANAGER
from tests.conftest import login


def test_manager_role_permissions():
    perms = permissions_for_role(ROLE_MANAGER)
    assert PERM_REPORTS in perms
    assert "items.write" not in perms
    assert "items.stock" in perms
    assert "users.manage" not in perms


def test_auth_me_includes_permissions(client):
    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200, response.get_json()
    user = response.get_json()["data"]
    assert user["role"] == ROLE_MANAGER
    assert "permissions" in user
    assert PERM_REPORTS in user["permissions"]
    assert "users.manage" not in user["permissions"]


def test_owner_can_create_manager(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "Ops Manager",
            "email": "ops.manager@hotela.com",
            "password": "Manager@12345",
            "role": "MANAGER",
        },
    )
    assert response.status_code == 201, response.get_json()
    assert response.get_json()["data"]["role"] == "MANAGER"


def test_manager_can_access_reports(client):
    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.get("/api/v1/reports/summary", headers=headers)
    assert response.status_code == 200, response.get_json()


def test_manager_can_list_stock_movements(client):
    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.get("/api/v1/stock-movements", headers=headers)
    assert response.status_code == 200, response.get_json()


def test_manager_cannot_access_users(client):
    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 403, response.get_json()


def test_manager_cannot_access_audit_logs(client):
    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.get("/api/v1/audit-logs", headers=headers)
    assert response.status_code == 403, response.get_json()


def test_manager_cannot_create_item(client):
    owner_headers = login(client, "owner@hotela.com", "Owner@12345")
    cat = client.post(
        "/api/v1/categories",
        headers=owner_headers,
        json={"name": "Manager Test Category"},
    )
    assert cat.status_code == 201, cat.get_json()
    category_id = cat.get_json()["data"]["id"]

    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": "Blocked Item",
            "category_id": category_id,
            "price": "100",
            "gst_percentage": "5",
        },
    )
    assert response.status_code == 403, response.get_json()


def test_manager_can_adjust_stock(client):
    owner_headers = login(client, "owner@hotela.com", "Owner@12345")
    cat = client.post(
        "/api/v1/categories",
        headers=owner_headers,
        json={"name": "Stock Test Category"},
    )
    category_id = cat.get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner_headers,
        json={
            "name": "Stock Item",
            "category_id": category_id,
            "price": "50",
            "gst_percentage": "5",
            "stock_quantity": "10",
        },
    )
    assert item.status_code == 201, item.get_json()
    item_id = item.get_json()["data"]["id"]

    headers = login(client, "manager@hotela.com", "Manager@12345")
    response = client.post(
        f"/api/v1/items/{item_id}/adjust-stock",
        headers=headers,
        json={"delta": "-1", "reason": "Manager adjustment"},
    )
    assert response.status_code == 200, response.get_json()
    assert float(response.get_json()["data"]["stock_quantity"]) == 9.0


def test_billing_user_cannot_access_reports(client):
    headers = login(client, "billing@hotela.com", "Billing@12345")
    response = client.get("/api/v1/reports/summary", headers=headers)
    assert response.status_code == 403, response.get_json()
