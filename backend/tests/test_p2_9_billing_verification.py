"""P2-9 billing verification: cart remove ≠ catalog delete; sample totals."""

from app.extensions import db
from app.models.item import Item
from tests.conftest import login


def test_omitting_cart_line_does_not_delete_catalog_item(client):
    """Simulate removing Biscuits from the cart before finalize.

    Frontend only drops the line from cart state; the API must never soft-delete
    catalog items that were merely not included on the bill.
    """
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")

    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Snacks P29"},
    ).get_json()["data"]["id"]

    biscuits = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Biscuits",
            "category_id": category_id,
            "price": 20,
            "gst_percentage": 5,
        },
    ).get_json()["data"]
    tea = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Tea",
            "category_id": category_id,
            "price": 15,
            "gst_percentage": 5,
        },
    ).get_json()["data"]

    # Cart had Biscuits + Tea; user removed Biscuits → bill only Tea
    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "reference": "COUNTER-1",
            "payment_method": "cash",
            "discount": 0,
            "items": [{"item_id": tea["id"], "quantity": 2}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    data = bill.get_json()["data"]
    assert data["payment_method"] == "cash"
    assert len(data["items"]) == 1
    assert data["items"][0]["item_name"] == "Tea"
    assert data["subtotal"] == 30.0
    # Line GST 5% on ₹30 = ₹1.50 → ₹31.50, then bill rounds to nearest rupee
    assert data["grand_total"] == 32.0
    assert float(data.get("round_off", 0)) == 0.5

    biscuits_row = db.session.get(Item, biscuits["id"])
    assert biscuits_row is not None
    assert biscuits_row.is_active is True
    assert biscuits_row.name == "Biscuits"

    still_listed = client.get(
        "/api/v1/items",
        headers=billing,
        query_string={"is_active": "true", "q": "Biscuits"},
    ).get_json()["data"]
    assert any(row["id"] == biscuits["id"] for row in still_listed)


def test_online_bill_totals_with_discount(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Drinks P29"},
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Cold Coffee",
            "category_id": category_id,
            "price": 100,
            "gst_percentage": 5,
        },
    ).get_json()["data"]

    response = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "online",
            "discount": 10,
            "items": [{"item_id": item["id"], "quantity": 1}],
        },
    )
    assert response.status_code == 201, response.get_json()
    bill = response.get_json()["data"]
    assert bill["payment_method"] == "online"
    assert bill["payment_method_label"] == "Online"
    assert bill["subtotal"] == 100.0
    assert bill["discount"] == 10.0
    assert bill["taxable_amount"] == 90.0
    # 90 + 5% = 94.5 → rounds to nearest rupee
    assert bill["grand_total"] == 95.0
    assert float(bill.get("round_off", 0)) == 0.5
