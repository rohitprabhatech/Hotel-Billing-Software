"""Sprint BIZ-04 — customer master CRM."""

from tests.conftest import login


def _create_category(client, headers, name="CRM Category"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _create_item(client, headers, category_id, name="CRM Item"):
    response = client.post(
        "/api/v1/items",
        headers=headers,
        json={
            "name": name,
            "category_id": category_id,
            "price": "100",
            "gst_percentage": "5",
        },
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def test_create_and_list_customers(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    created = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "name": "Ravi Sharma",
            "phone_country_code": "91",
            "phone": "9876501234",
            "email": "ravi@example.com",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["name"] == "Ravi Sharma"
    assert body["phone_masked"]
    assert body["is_active"] is True

    listing = client.get("/api/v1/customers?q=Ravi", headers=headers)
    assert listing.status_code == 200, listing.get_json()
    assert any(row["name"] == "Ravi Sharma" for row in listing.get_json()["data"])


def test_duplicate_phone_rejected(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    payload = {
        "name": "Customer One",
        "phone_country_code": "91",
        "phone": "9876509999",
    }
    first = client.post("/api/v1/customers", headers=headers, json=payload)
    assert first.status_code == 201, first.get_json()

    second = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": "Customer Two", **payload},
    )
    assert second.status_code == 409, second.get_json()


def test_bill_links_customer_and_keeps_ad_hoc_fields(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner)
    item_id = _create_item(client, owner, category_id)

    customer = client.post(
        "/api/v1/customers",
        headers=owner,
        json={
            "name": "Walk-in Regular",
            "phone_country_code": "91",
            "phone": "9876512345",
            "email": "regular@example.com",
        },
    )
    assert customer.status_code == 201, customer.get_json()
    customer_id = customer.get_json()["data"]["id"]

    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "customer_id": customer_id,
            "customer_name": "Counter Override",
            "items": [{"item_id": item_id, "quantity": 1}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    data = bill.get_json()["data"]
    assert data["customer_id"] == customer_id
    assert data["customer_name"] == "Counter Override"

    ad_hoc = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "customer_name": "Guest",
            "customer_phone_country_code": "91",
            "customer_phone": "9123456789",
            "items": [{"item_id": item_id, "quantity": 1}],
        },
    )
    assert ad_hoc.status_code == 201, ad_hoc.get_json()
    assert ad_hoc.get_json()["data"]["customer_id"] is None
    assert ad_hoc.get_json()["data"]["customer_name"] == "Guest"


def test_customer_bills_history(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = _create_category(client, owner, "History Category")
    item_id = _create_item(client, owner, category_id, "History Item")

    customer = client.post(
        "/api/v1/customers",
        headers=owner,
        json={"name": "History Customer", "phone_country_code": "91", "phone": "9876522222"},
    )
    customer_id = customer.get_json()["data"]["id"]

    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={"customer_id": customer_id, "items": [{"item_id": item_id, "quantity": 1}]},
    )
    assert bill.status_code == 201, bill.get_json()

    history = client.get(f"/api/v1/customers/{customer_id}/bills", headers=owner)
    assert history.status_code == 200, history.get_json()
    assert history.get_json()["meta"]["total"] >= 1


def test_customer_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")

    created = client.post(
        "/api/v1/customers",
        headers=owner_a,
        json={"name": "Tenant A Customer", "phone_country_code": "91", "phone": "9876533333"},
    )
    customer_id = created.get_json()["data"]["id"]

    denied = client.get(f"/api/v1/customers/{customer_id}", headers=owner_b)
    assert denied.status_code == 404, denied.get_json()


def test_deactivate_customer_soft_delete(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    created = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": "Inactive Soon", "phone_country_code": "91", "phone": "9876544444"},
    )
    customer_id = created.get_json()["data"]["id"]

    deleted = client.delete(f"/api/v1/customers/{customer_id}", headers=headers)
    assert deleted.status_code == 200, deleted.get_json()
    assert deleted.get_json()["data"]["is_active"] is False

    still_there = client.get(f"/api/v1/customers/{customer_id}", headers=headers)
    assert still_there.status_code == 200, still_there.get_json()
    assert still_there.get_json()["data"]["is_active"] is False


def test_billing_user_can_create_customer(client):
    headers = login(client, "billing@hotela.com", "Billing@12345")
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": "Counter Customer", "phone_country_code": "91", "phone": "9876555555"},
    )
    assert response.status_code == 201, response.get_json()
