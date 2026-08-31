"""Reproduce TEST 8 credit bill with warehouse stock mismatch."""

from decimal import Decimal

from app.extensions import db
from app.models.warehouse import Warehouse, WarehouseStock
from app.utils.ids import new_uuid
from tests.conftest import login


def _switch(client, headers, business_type="hardware"):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Pipes"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name="GI Pipe 1 inch", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "450",
        "gst_percentage": "18",
        "stock_quantity": "100",
        "uom": "m",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _customer(client, headers, name="Sharma Contractor"):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "+91", "phone": "9876543210"},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_credit_pipe_transport_happy_path(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    pipe = _item(client, owner, cat_id)
    customer = _customer(client, owner)

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": pipe["id"], "quantity": "3"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
            "transport_charge": "20",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert Decimal(str(bill.get_json()["data"]["grand_total"])) == Decimal("1613")


def test_credit_pipe_transport_with_empty_warehouse_stock(client):
    """Mimic MAIN warehouse existing but item stock not mirrored in warehouse."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    pipe = _item(client, owner, cat_id)
    customer = _customer(client, owner)

    # Force empty MAIN warehouse (warehouse module on for hardware).
    wh = Warehouse(
        id=new_uuid(),
        tenant_id=pipe["tenant_id"] if "tenant_id" in pipe else None,
        code="MAIN",
        name="Main warehouse",
        is_default=True,
        is_active=True,
    )
    # Resolve tenant id from API
    me = client.get("/api/v1/tenants/me", headers=owner)
    tenant_id = me.get_json()["data"]["id"]
    wh.tenant_id = tenant_id
    db.session.add(wh)
    db.session.flush()
    db.session.add(
        WarehouseStock(
            id=new_uuid(),
            tenant_id=tenant_id,
            warehouse_id=wh.id,
            item_id=pipe["id"],
            quantity=Decimal("0"),
        )
    )
    db.session.commit()

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": pipe["id"], "quantity": "3"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
            "transport_charge": "20",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert Decimal(str(bill.get_json()["data"]["grand_total"])) == Decimal("1613")
