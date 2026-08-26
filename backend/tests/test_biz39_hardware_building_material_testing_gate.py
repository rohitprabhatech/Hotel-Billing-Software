"""Sprint BIZ-39 — hardware + building material testing gate.

Regression matrix across BIZ-35 … BIZ-38: measurement UoM billing, quotations,
delivery challans, transport charges, trade credit, warehouses/transfers,
module matrix, isolation, permissions, audit, and API contracts.

Run full phase gate from backend/:
  python -m pytest tests/test_biz35_length_weight_area_uom.py \\
    tests/test_biz36_quotation_delivery_challan.py \\
    tests/test_biz37_trade_credit_transport.py \\
    tests/test_biz38_warehouse_stock_foundation.py \\
    tests/test_biz39_hardware_building_material_testing_gate.py -q
"""

from decimal import Decimal

from tests.conftest import login


def _switch(client, headers, business_type: str):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Gate Materials"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
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


def _customer(client, headers, name, phone):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": phone},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _supplier(client, headers, name):
    response = client.post("/api/v1/suppliers", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_restaurant_hardware_vertical_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    for path in (
        "/api/v1/hardware/units",
        "/api/v1/quotations",
        "/api/v1/challans",
        "/api/v1/warehouses",
        "/api/v1/stock-transfers",
    ):
        assert client.get(path, headers=owner).status_code == 403, path


def test_gate_module_matrix_hardware_vs_building_material(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")
    hardware = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in (
        "uom_measurement",
        "quotation",
        "delivery_challan",
        "customer_credit",
        "transport_charges",
        "bulk_pricing",
    ):
        assert code in hardware, code
    assert "warehouse" not in hardware
    assert "serial_imei" not in hardware
    assert "order_channels" not in hardware

    _switch(client, owner, "building_material")
    building = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in (
        "uom_measurement",
        "quotation",
        "delivery_challan",
        "warehouse",
        "customer_credit",
        "transport_charges",
    ):
        assert code in building, code
    assert "bulk_pricing" not in building


def test_gate_pipe_quote_and_hardware_pos_catalog(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner, "Gate-Pipes")
    pipe = _item(client, owner, cat_id, "GI Pipe Gate", price="450", uom="m")

    units = client.get("/api/v1/hardware/units", headers=billing)
    assert units.status_code == 200, units.get_json()
    assert units.get_json()["success"] is True
    assert "sqft" in units.get_json()["data"]["area_uoms"]

    catalog = client.get("/api/v1/hardware/pos-catalog", headers=billing)
    assert catalog.status_code == 200, catalog.get_json()
    ids = {row["id"] for row in catalog.get_json()["data"]["items"]}
    assert pipe["id"] in ids

    quote = client.post(
        "/api/v1/hardware/quote",
        headers=billing,
        json={"item_id": pipe["id"], "quantity": "10"},
    )
    assert quote.status_code == 200, quote.get_json()
    body = quote.get_json()["data"]
    assert body["line_total"] == 4500.0
    assert body["unit_price"] == 450.0


def test_gate_quote_challan_convert_with_transport(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner, "Gate-Docs")
    item = _item(client, owner, cat_id, "MS Rod Gate", price="100", gst_percentage="0")

    quote = client.post(
        "/api/v1/quotations",
        headers=owner,
        json={
            "customer_name": "Gate Contractor",
            "items": [{"item_id": item["id"], "quantity": "4"}],
        },
    )
    assert quote.status_code == 201, quote.get_json()
    assert quote.get_json()["success"] is True
    qid = quote.get_json()["data"]["id"]
    assert quote.get_json()["data"]["quotation_number"].startswith("QT-")

    converted_q = client.post(
        f"/api/v1/quotations/{qid}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted_q.status_code == 200, converted_q.get_json()
    assert converted_q.get_json()["data"]["quotation"]["status"] == "CONVERTED"
    assert len(converted_q.get_json()["data"]["bill"]["items"]) == 1
    assert converted_q.get_json()["data"]["bill"]["items"][0]["quantity"] == 4.0

    challan = client.post(
        "/api/v1/challans",
        headers=owner,
        json={
            "customer_name": "Gate Site",
            "transport_charge": "50",
            "items": [{"item_id": item["id"], "quantity": "2"}],
        },
    )
    assert challan.status_code == 201, challan.get_json()
    cid = challan.get_json()["data"]["id"]
    assert Decimal(str(challan.get_json()["data"]["transport_charge"])) == Decimal("50.00")

    pdf = client.get(f"/api/v1/challans/{cid}/pdf", headers=owner)
    assert pdf.status_code == 200
    assert pdf.data[:4] == b"%PDF"

    converted_c = client.post(
        f"/api/v1/challans/{cid}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted_c.status_code == 200, converted_c.get_json()
    bill = converted_c.get_json()["data"]["bill"]
    assert Decimal(str(bill["transport_charge"])) == Decimal("50.00")
    assert Decimal(str(bill["grand_total"])) == Decimal("250")  # 200 + 50


def test_gate_trade_credit_customer_and_supplier(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner, "Gate-Credit")
    item = _item(client, owner, cat_id, "Credit Pipe", price="100", gst_percentage="0")
    customer = _customer(client, owner, "Gate Credit Cust", "9000000039")
    supplier = _supplier(client, owner, "Gate Steel Depot")

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "3"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
            "transport_charge": "20",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert Decimal(str(bill.get_json()["data"]["grand_total"])) == Decimal("320")

    outstanding = client.get("/api/v1/customers/outstanding", headers=owner)
    assert outstanding.status_code == 200, outstanding.get_json()
    match = next(row for row in outstanding.get_json()["data"] if row["id"] == customer["id"])
    assert Decimal(str(match["balance"])) == Decimal("320.00")

    purchase = client.post(
        "/api/v1/purchases",
        headers=owner,
        json={
            "supplier_id": supplier["id"],
            "payment_method": "credit",
            "items": [{"item_id": item["id"], "quantity": "2", "unit_cost": "40"}],
        },
    )
    assert purchase.status_code == 201, purchase.get_json()

    supp_out = client.get("/api/v1/suppliers/outstanding", headers=owner)
    assert supp_out.status_code == 200, supp_out.get_json()
    smatch = next(row for row in supp_out.get_json()["data"] if row["id"] == supplier["id"])
    assert Decimal(str(smatch["balance"])) == Decimal("80.00")

    paid = client.post(
        f"/api/v1/suppliers/{supplier['id']}/payments",
        headers=owner,
        json={"amount": "30", "collection_method": "cash"},
    )
    assert paid.status_code == 201, paid.get_json()
    assert paid.get_json()["success"] is True


def test_gate_warehouse_transfer_and_sell(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "building_material")
    cat_id = _category(client, owner, "Gate-WH")
    item = _item(client, owner, cat_id, "Gate Cement", price="80", gst_percentage="0", stock_quantity="30")

    warehouses = client.get("/api/v1/warehouses", headers=owner)
    assert warehouses.status_code == 200, warehouses.get_json()
    assert warehouses.get_json()["success"] is True
    main = next(row for row in warehouses.get_json()["data"] if row["is_default"])

    yard = client.post(
        "/api/v1/warehouses",
        headers=owner,
        json={"code": "GATEY", "name": "Gate Yard"},
    )
    assert yard.status_code == 201, yard.get_json()
    yard_id = yard.get_json()["data"]["id"]

    transfer = client.post(
        "/api/v1/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": yard_id,
            "items": [{"item_id": item["id"], "quantity": "10"}],
        },
    )
    assert transfer.status_code == 201, transfer.get_json()
    assert transfer.get_json()["data"]["transfer_number"].startswith("ST-")

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "4"}],
            "payment_method": "cash",
            "warehouse_id": yard_id,
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert bill.get_json()["data"]["warehouse_id"] == yard_id

    stocks = client.get(
        "/api/v1/warehouses/stocks",
        headers=owner,
        query_string={"item_id": item["id"]},
    )
    by_wh = {
        row["warehouse_id"]: Decimal(str(row["quantity"]))
        for row in stocks.get_json()["data"]
    }
    assert by_wh[yard_id] == Decimal("6")
    assert by_wh[main["id"]] == Decimal("20")

    # Hardware cannot use warehouses
    _switch(client, owner, "hardware")
    assert client.get("/api/v1/warehouses", headers=owner).status_code == 403


def test_gate_permissions_billing_cannot_write_docs(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner, "Gate-Perm")
    item = _item(client, owner, cat_id, "Perm Pipe", price="50", gst_percentage="0")

    denied = client.post(
        "/api/v1/quotations",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": "1"}]},
    )
    assert denied.status_code == 403, denied.get_json()

    denied_c = client.post(
        "/api/v1/challans",
        headers=billing,
        json={"items": [{"item_id": item["id"], "quantity": "1"}]},
    )
    assert denied_c.status_code == 403, denied_c.get_json()

    ok = client.post(
        "/api/v1/quotations",
        headers=manager,
        json={"items": [{"item_id": item["id"], "quantity": "1"}]},
    )
    assert ok.status_code == 201, ok.get_json()

    listing = client.get("/api/v1/quotations", headers=billing)
    assert listing.status_code == 200, listing.get_json()


def test_gate_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "hardware")
    _switch(client, owner_b, "hardware")

    cat_a = _category(client, owner_a, "Gate-Iso-A")
    item_a = _item(client, owner_a, cat_a, "Iso Pipe A")
    quote = client.post(
        "/api/v1/quotations",
        headers=owner_a,
        json={"items": [{"item_id": item_a["id"], "quantity": "1"}]},
    )
    assert quote.status_code == 201, quote.get_json()
    qid = quote.get_json()["data"]["id"]

    foreign = client.get(f"/api/v1/quotations/{qid}", headers=owner_b)
    assert foreign.status_code == 404, foreign.get_json()

    convert = client.post(
        f"/api/v1/quotations/{qid}/convert",
        headers=owner_b,
        json={"payment_method": "cash"},
    )
    assert convert.status_code == 404, convert.get_json()


def test_gate_audit_and_api_envelopes(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "building_material")
    cat_id = _category(client, owner, "Gate-Audit")
    item = _item(client, owner, cat_id, "Audit Bag", stock_quantity="20")

    wh_list = client.get("/api/v1/warehouses", headers=owner)
    assert wh_list.get_json()["success"] is True
    main = next(row for row in wh_list.get_json()["data"] if row["is_default"])
    other = client.post(
        "/api/v1/warehouses",
        headers=owner,
        json={"code": "AUD2", "name": "Audit Bay"},
    )
    assert other.get_json()["success"] is True

    transfer = client.post(
        "/api/v1/stock-transfers",
        headers=owner,
        json={
            "from_warehouse_id": main["id"],
            "to_warehouse_id": other.get_json()["data"]["id"],
            "items": [{"item_id": item["id"], "quantity": "5"}],
        },
    )
    assert transfer.get_json()["success"] is True

    actions = _audit_actions(client, owner)
    assert "CREATE_WAREHOUSE" in actions or "CREATE_STOCK_TRANSFER" in actions
    assert "CREATE_STOCK_TRANSFER" in actions

    quote = client.post(
        "/api/v1/quotations",
        headers=owner,
        json={"items": [{"item_id": item["id"], "quantity": "1"}]},
    )
    assert quote.get_json()["success"] is True
    assert "CREATE_QUOTATION" in _audit_actions(client, owner, action="CREATE_QUOTATION")
