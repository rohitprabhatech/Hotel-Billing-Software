"""Additional Sprint 9 production-readiness checks."""

from decimal import Decimal

from app.utils.money import calculate_bill_totals
from tests.conftest import login


def test_inactive_user_cannot_login(client, app):
    from app.extensions import db
    from app.models.user import User

    with app.app_context():
        user = (
            db.session.query(User)
            .filter(User.email == "billing@hotela.com")
            .first()
        )
        user.is_active = False
        db.session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "billing@hotela.com", "password": "Billing@12345"},
    )
    assert response.status_code == 401


def test_mixed_gst_rates_calculation():
    result = calculate_bill_totals(
        [
            {
                "item_id": "1",
                "item_name": "Thali",
                "quantity": 1,
                "unit_price": 400,
                "gst_percentage": 5,
            },
            {
                "item_id": "2",
                "item_name": "Water",
                "quantity": 2,
                "unit_price": 20,
                "gst_percentage": 0,
            },
        ],
        discount_amount=0,
    )
    assert result["subtotal"] == Decimal("440.00")
    # taxable same as subtotal; cgst/sgst only from 5% item: 400 * 2.5% = 10 each
    assert result["cgst_amount"] == Decimal("10.00")
    assert result["sgst_amount"] == Decimal("10.00")
    assert result["grand_total"] == Decimal("460.00")


def test_no_hard_delete_bill_endpoint(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Prod Cat"},
    ).get_json()["data"]["id"]
    item_id = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Prod Item",
            "category_id": category_id,
            "price": 100,
            "gst_percentage": 5,
        },
    ).get_json()["data"]["id"]
    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={"items": [{"item_id": item_id, "quantity": 1}]},
    ).get_json()["data"]

    response = client.delete(f"/api/v1/bills/{bill['id']}", headers=owner)
    assert response.status_code in {404, 405}

    still = client.get(f"/api/v1/bills/{bill['id']}", headers=owner)
    assert still.status_code == 200
    assert still.get_json()["data"]["status"] == "FINALIZED"


def test_password_hash_not_exposed(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@hotela.com", "password": "Owner@12345"},
    )
    payload = response.get_json()
    raw = str(payload)
    assert "password_hash" not in raw
    assert "password" not in payload["data"]["user"]
