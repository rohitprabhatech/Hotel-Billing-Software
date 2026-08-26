"""Sprint BIZ-52 — wholesale sales orders and purchase orders."""

from tests.conftest import login


def _switch_wholesale(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "wholesale"},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Trade"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "200",
        "gst_percentage": "0",
        "stock_quantity": "40",
        "uom": "pcs",
        "cost_price": "120",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _customer(client, headers, name="Dealer", phone="9000000060"):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": phone},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _supplier(client, headers, name="Vendor Co"):
    response = client.post("/api/v1/suppliers", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_restaurant_so_po_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=owner,
        json={"business_type": "hotel_restaurant"},
    )
    assert client.get("/api/v1/sales-orders", headers=owner).status_code == 403
    assert client.get("/api/v1/purchase-orders", headers=owner).status_code == 403


def test_sales_order_convert_to_bill(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_wholesale(client, owner)
    cat_id = _category(client, owner)
    widget = _item(client, owner, cat_id, "SO Widget", stock_quantity="10")
    buyer = _customer(client, owner)

    denied = client.post(
        "/api/v1/sales-orders",
        headers=billing,
        json={
            "customer_id": buyer["id"],
            "items": [{"item_id": widget["id"], "quantity": "2"}],
        },
    )
    assert denied.status_code == 403, denied.get_json()

    created = client.post(
        "/api/v1/wholesale/sales-orders",
        headers=owner,
        json={
            "customer_id": buyer["id"],
            "customer_name": buyer["name"],
            "items": [{"item_id": widget["id"], "quantity": "2", "unit_price": "180"}],
            "notes": "Dealer order",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["order_number"].startswith("SO-")
    assert body["status"] == "DRAFT"
    assert len(body["items"]) == 1
    oid = body["id"]

    confirmed = client.patch(
        f"/api/v1/sales-orders/{oid}/status",
        headers=owner,
        json={"status": "CONFIRMED"},
    )
    assert confirmed.status_code == 200, confirmed.get_json()
    assert confirmed.get_json()["data"]["status"] == "CONFIRMED"

    converted = client.post(
        f"/api/v1/sales-orders/{oid}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted.status_code == 200, converted.get_json()
    payload = converted.get_json()["data"]
    assert payload["sales_order"]["status"] == "CONVERTED"
    assert payload["sales_order"]["bill_id"] == payload["bill"]["id"]
    assert payload["bill"]["items"][0]["quantity"] == 2.0

    stock = client.get(f"/api/v1/items/{widget['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 8.0


def test_purchase_order_convert_to_purchase(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_wholesale(client, owner)
    cat_id = _category(client, owner, "PO Cat")
    item = _item(client, owner, cat_id, "PO Item", stock_quantity="5", price="150")
    supplier = _supplier(client, owner)

    denied = client.post(
        "/api/v1/purchase-orders",
        headers=billing,
        json={
            "supplier_id": supplier["id"],
            "items": [{"item_id": item["id"], "quantity": "3", "unit_cost": "90"}],
        },
    )
    assert denied.status_code == 403, denied.get_json()

    created = client.post(
        "/api/v1/wholesale/purchase-orders",
        headers=owner,
        json={
            "supplier_id": supplier["id"],
            "items": [{"item_id": item["id"], "quantity": "3", "unit_cost": "90"}],
            "notes": "Restock",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["order_number"].startswith("PO-")
    assert body["grand_total"] == 270.0
    oid = body["id"]

    converted = client.post(
        f"/api/v1/purchase-orders/{oid}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted.status_code == 200, converted.get_json()
    payload = converted.get_json()["data"]
    assert payload["purchase_order"]["status"] == "CONVERTED"
    assert payload["purchase_order"]["purchase_id"] == payload["purchase"]["id"]

    stock = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 8.0  # 5 + 3


def test_so_po_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_wholesale(client, owner_a)
    _switch_wholesale(client, owner_b)
    cat_id = _category(client, owner_a)
    item = _item(client, owner_a, cat_id, "Iso Item")

    so = client.post(
        "/api/v1/sales-orders",
        headers=owner_a,
        json={"items": [{"item_id": item["id"], "quantity": "1"}]},
    )
    assert so.status_code == 201, so.get_json()
    so_id = so.get_json()["data"]["id"]

    supplier = _supplier(client, owner_a, "Iso Supplier")
    po = client.post(
        "/api/v1/purchase-orders",
        headers=owner_a,
        json={
            "supplier_id": supplier["id"],
            "items": [{"item_id": item["id"], "quantity": "1", "unit_cost": "50"}],
        },
    )
    assert po.status_code == 201, po.get_json()
    po_id = po.get_json()["data"]["id"]

    assert client.get(f"/api/v1/sales-orders/{so_id}", headers=owner_b).status_code == 404
    assert client.get(f"/api/v1/purchase-orders/{po_id}", headers=owner_b).status_code == 404


def test_cannot_convert_cancelled_sales_order(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_wholesale(client, owner)
    cat_id = _category(client, owner, "Cancel Cat")
    item = _item(client, owner, cat_id, "Cancel Item")
    created = client.post(
        "/api/v1/sales-orders",
        headers=owner,
        json={"items": [{"item_id": item["id"], "quantity": "1"}]},
    )
    oid = created.get_json()["data"]["id"]
    client.patch(
        f"/api/v1/sales-orders/{oid}/status",
        headers=owner,
        json={"status": "CANCELLED"},
    )
    blocked = client.post(
        f"/api/v1/sales-orders/{oid}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert blocked.status_code == 400, blocked.get_json()
