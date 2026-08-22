"""Sprint BIZ-06 — purchases module."""

from tests.conftest import login


def _create_category(client, headers, name="Purchase Category"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _create_item(client, headers, category_id, name="Purchase Item", stock="10"):
    response = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": name,
            "category_id": category_id,
            "price": "100",
            "gst_percentage": "5",
            "stock_quantity": stock,
            "cost_price": "50",
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _create_supplier(client, headers, name="Purchase Supplier"):
    response = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": "9876677777"},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _create_purchase(client, headers, item_id, supplier_id=None, quantity="5", unit_cost="40"):
    payload = {
        "supplier_id": supplier_id,
        "invoice_number": "INV-001",
        "items": [{"item_id": item_id, "quantity": quantity, "unit_cost": unit_cost}],
    }
    response = client.post("/api/v1/purchases", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_create_purchase_increases_stock_and_writes_ledger(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id, stock="10")
    supplier = _create_supplier(client, owner)

    purchase = _create_purchase(client, owner, item["id"], supplier_id=supplier["id"])
    assert purchase["purchase_number"].startswith("PO-")
    assert purchase["status"] == "FINALIZED"
    assert purchase["supplier_name"] == supplier["name"]
    assert purchase["total_amount"] == 200.0
    assert len(purchase["items"]) == 1

    item_after = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert item_after["stock_quantity"] == 15.0
    assert item_after["cost_price"] == 40.0

    movements = client.get(
        "/api/v1/stock-movements",
        headers=owner,
        query_string={"item_id": item["id"], "source": "PURCHASE"},
    )
    assert movements.status_code == 200, movements.get_json()
    rows = movements.get_json()["data"]
    assert any(
        row["source"] == "PURCHASE"
        and row["reference_type"] == "PURCHASE"
        and row["reference_id"] == purchase["id"]
        and row["delta"] == 5.0
        for row in rows
    )


def test_cancel_purchase_reverses_stock(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id, stock="10")
    purchase = _create_purchase(client, owner, item["id"])

    cancelled = client.post(
        f"/api/v1/purchases/{purchase['id']}/cancel",
        headers=owner,
        json={"reason": "Wrong supplier invoice"},
    )
    assert cancelled.status_code == 200, cancelled.get_json()
    body = cancelled.get_json()["data"]
    assert body["status"] == "CANCELLED"
    assert body["cancellation_reason"] == "Wrong supplier invoice"

    item_after = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert item_after["stock_quantity"] == 10.0

    movements = client.get(
        "/api/v1/stock-movements",
        headers=owner,
        query_string={"item_id": item["id"], "source": "PURCHASE_CANCEL"},
    ).get_json()["data"]
    assert any(row["source"] == "PURCHASE_CANCEL" and row["delta"] == -5.0 for row in movements)


def test_cancel_blocked_when_stock_insufficient(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id, stock="10")
    purchase = _create_purchase(client, owner, item["id"], quantity="8")

    sold = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "items": [{"item_id": item["id"], "quantity": "11"}],
            "payment_method": "cash",
        },
    )
    assert sold.status_code == 201, sold.get_json()

    blocked = client.post(
        f"/api/v1/purchases/{purchase['id']}/cancel",
        headers=owner,
        json={"reason": "Should fail"},
    )
    assert blocked.status_code == 400, blocked.get_json()


def test_purchase_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    category_id = _create_category(client, owner_a)
    item = _create_item(client, owner_a, category_id)
    purchase = _create_purchase(client, owner_a, item["id"])

    denied = client.get(f"/api/v1/purchases/{purchase['id']}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_manager_can_manage_purchases(client):
    manager = login(client, "manager@hotela.com", "Manager@12345")
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item = _create_item(client, owner, category_id, name="Manager Purchase Item")

    created = _create_purchase(client, manager, item["id"])
    assert created["status"] == "FINALIZED"

    listing = client.get("/api/v1/purchases", headers=manager)
    assert listing.status_code == 200, listing.get_json()
    assert any(row["id"] == created["id"] for row in listing.get_json()["data"])


def test_billing_user_denied_purchases(client):
    billing = login(client, "billing@hotela.com", "Billing@12345")
    denied = client.get("/api/v1/purchases", headers=billing)
    assert denied.status_code == 403, denied.get_json()
