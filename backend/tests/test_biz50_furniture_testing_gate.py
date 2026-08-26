"""Sprint BIZ-50 — furniture testing gate.

Regression matrix across BIZ-47 … BIZ-49: product attributes, custom orders,
delivery board, installation from orders, quotations (BIZ-36 reuse), module
matrix, isolation, permissions, audit, and API contracts.

Run full phase gate from backend/:
  python -m pytest tests/test_biz47_furniture_product_attributes.py \\
    tests/test_biz48_furniture_custom_orders.py \\
    tests/test_biz49_furniture_delivery_installation.py \\
    tests/test_biz50_furniture_quotations.py \\
    tests/test_biz50_furniture_testing_gate.py -q
"""

from datetime import datetime, timedelta

from tests.conftest import login


def _switch(client, headers, business_type: str):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Gate Furniture"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _sofa(client, headers, category_id, name="Gate Sofa", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "32000",
        "gst_percentage": "18",
        "stock_quantity": "4",
        "uom": "pcs",
        "dimension_length": "84",
        "dimension_width": "36",
        "dimension_height": "32",
        "material": "Teak",
        "color": "Walnut",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def _ready_order(client, headers, *, title="Gate Wardrobe"):
    delivery = (datetime.utcnow() + timedelta(days=5)).isoformat()
    created = client.post(
        "/api/v1/furniture/custom-orders",
        headers=headers,
        json={
            "title": title,
            "size": "180×60×210",
            "flavor": "Teak",
            "customer_name": "Gate Customer",
            "customer_phone": "9000000050",
            "total_amount": "42000",
            "advance_amount": "12000",
            "delivery_at": delivery,
        },
    )
    assert created.status_code == 201, created.get_json()
    oid = created.get_json()["data"]["id"]
    manager = login(client, "manager@hotela.com", "Manager@12345")
    for status in ("CONFIRMED", "IN_PRODUCTION", "READY"):
        updated = client.patch(
            f"/api/v1/custom-orders/{oid}/status",
            headers=manager,
            json={"status": status},
        )
        assert updated.status_code == 200, updated.get_json()
    return oid


def test_restaurant_furniture_vertical_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    for path in (
        "/api/v1/furniture/custom-orders",
        "/api/v1/furniture/deliveries",
        "/api/v1/furniture/quotations",
        "/api/v1/deliveries",
        "/api/v1/quotations",
    ):
        assert client.get(path, headers=owner).status_code == 403, path


def test_gate_module_matrix_furniture(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "furniture")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in (
        "furniture_attributes",
        "custom_orders",
        "quotation",
        "delivery_tracking",
        "installation",
    ):
        assert code in modules, code
    for code in (
        "book_metadata",
        "warehouse",
        "delivery_challan",
        "serial_imei",
        "production",
    ):
        assert code not in modules, code


def test_gate_furniture_attributes_search_and_sell(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "furniture")
    cat_id = _category(client, owner)
    sofa = _sofa(client, owner, cat_id, material="Rosewood", color="Ebony")

    search = client.get("/api/v1/items", headers=owner, query_string={"q": "Rosewood"})
    assert search.status_code == 200, search.get_json()
    assert any(row["id"] == sofa["id"] for row in search.get_json()["data"])

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": sofa["id"], "quantity": "1"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    stock = client.get(f"/api/v1/items/{sofa['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 3.0


def test_gate_custom_order_advance_and_delivery_pipeline(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "furniture")
    oid = _ready_order(client, billing)

    blocked = client.patch(
        f"/api/v1/custom-orders/{oid}/status",
        headers=owner,
        json={"status": "DELIVERED"},
    )
    assert blocked.status_code == 400, blocked.get_json()

    delivery = client.post(
        "/api/v1/furniture/deliveries",
        headers=owner,
        json={
            "custom_order_id": oid,
            "delivery_address": "Gate Address, Pune",
        },
    )
    assert delivery.status_code == 201, delivery.get_json()
    did = delivery.get_json()["data"]["id"]

    for status in ("OUT_FOR_DELIVERY", "DELIVERED"):
        updated = client.patch(
            f"/api/v1/deliveries/{did}/status",
            headers=owner,
            json={"status": status},
        )
        assert updated.status_code == 200, updated.get_json()

    order = client.get(f"/api/v1/custom-orders/{oid}", headers=owner).get_json()["data"]
    assert order["status"] == "DELIVERED"
    assert order["delivered_at"]


def test_gate_installation_from_ready_custom_order(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "furniture")
    oid = _ready_order(client, billing, title="Gate Kitchen")

    scheduled = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%dT10:00:00")
    created = client.post(
        "/api/v1/furniture/installations",
        headers=owner,
        json={
            "custom_order_id": oid,
            "scheduled_at": scheduled,
            "install_address": "Gate Address",
            "technician_name": "Gate Tech",
        },
    )
    assert created.status_code == 201, created.get_json()
    body = created.get_json()["data"]
    assert body["custom_order_id"] == oid
    assert body["status"] == "SCHEDULED"


def test_gate_furniture_quotation_convert_and_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "furniture")
    cat_id = _category(client, owner, "Gate-Quote")
    table = _sofa(client, owner, cat_id, name="Gate Dining Table", price="18000", stock_quantity="2")

    denied = client.post(
        "/api/v1/furniture/quotations",
        headers=billing,
        json={
            "customer_name": "Billing blocked",
            "items": [{"item_id": table["id"], "quantity": "1"}],
        },
    )
    assert denied.status_code == 403, denied.get_json()

    created = client.post(
        "/api/v1/furniture/quotations",
        headers=owner,
        json={
            "customer_name": "Gate Buyer",
            "items": [{"item_id": table["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    qid = created.get_json()["data"]["id"]
    assert "CREATE_QUOTATION" in _audit_actions(client, owner, action="CREATE_QUOTATION")

    listed = client.get("/api/v1/quotations", headers=billing)
    assert listed.status_code == 200, listed.get_json()

    converted = client.post(
        f"/api/v1/furniture/quotations/{qid}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted.status_code == 200, converted.get_json()
    assert converted.get_json()["data"]["quotation"]["status"] == "CONVERTED"


def test_gate_custom_order_permissions(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "furniture")
    created = client.post(
        "/api/v1/custom-orders",
        headers=billing,
        json={
            "order_type": "furniture",
            "title": "Gate Chair",
            "total_amount": "8000",
            "advance_amount": "2000",
        },
    )
    assert created.status_code == 201, created.get_json()
    oid = created.get_json()["data"]["id"]

    denied = client.patch(
        f"/api/v1/custom-orders/{oid}/status",
        headers=billing,
        json={"status": "CONFIRMED"},
    )
    assert denied.status_code == 403, denied.get_json()

    ok = client.patch(
        f"/api/v1/custom-orders/{oid}/status",
        headers=manager,
        json={"status": "CONFIRMED"},
    )
    assert ok.status_code == 200, ok.get_json()


def test_gate_cross_tenant_furniture_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    billing_a = login(client, "billing@hotela.com", "Billing@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "furniture")
    _switch(client, owner_b, "furniture")

    oid = _ready_order(client, billing_a, title="Iso Piece")
    delivery = client.post(
        "/api/v1/deliveries",
        headers=owner_a,
        json={"custom_order_id": oid, "delivery_address": "Iso lane"},
    )
    assert delivery.status_code == 201, delivery.get_json()
    did = delivery.get_json()["data"]["id"]

    denied_order = client.get(f"/api/v1/custom-orders/{oid}", headers=owner_b)
    assert denied_order.status_code == 404, denied_order.get_json()
    denied_delivery = client.get(f"/api/v1/deliveries/{did}", headers=owner_b)
    assert denied_delivery.status_code == 404, denied_delivery.get_json()


def test_gate_delivery_billing_cannot_write(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "furniture")
    oid = _ready_order(client, billing)

    denied = client.post(
        "/api/v1/deliveries",
        headers=billing,
        json={"custom_order_id": oid, "delivery_address": "Billing blocked"},
    )
    assert denied.status_code == 403, denied.get_json()

    listed = client.get("/api/v1/furniture/deliveries", headers=billing)
    assert listed.status_code == 200, listed.get_json()


def test_gate_api_envelopes(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "furniture")
    orders = client.get("/api/v1/furniture/custom-orders", headers=owner)
    assert orders.status_code == 200, orders.get_json()
    assert orders.get_json()["success"] is True

    quotes = client.get("/api/v1/furniture/quotations", headers=owner)
    assert quotes.status_code == 200, quotes.get_json()
    assert quotes.get_json()["success"] is True

    deliveries = client.get("/api/v1/deliveries", headers=owner)
    assert deliveries.status_code == 200, deliveries.get_json()
    assert deliveries.get_json()["success"] is True
