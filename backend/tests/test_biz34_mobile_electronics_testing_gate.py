"""Sprint BIZ-34 — mobile + electronics testing gate.

Regression matrix across BIZ-29 … BIZ-33: serial/IMEI uniqueness, warranty,
returns/exchange, repairs, brand/model reports, installations, isolation,
permissions, audit, and API contracts.

Run full phase gate from backend/:
  python -m pytest tests/test_biz29_serial_units.py tests/test_biz30_warranty_accessories.py
    tests/test_biz31_repairs_serial_exchange.py tests/test_biz32_mobile_brand_model.py
    tests/test_biz33_installation_orders.py tests/test_biz34_mobile_electronics_testing_gate.py -q
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
    return response.get_json()["data"]


def _category(client, headers, name="Gate Devices"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "18000",
        "gst_percentage": "18",
        "tracks_serial": True,
        "stock_quantity": "0",
        "uom": "pcs",
        "brand": "Samsung",
        "model_name": "Galaxy Gate",
        "warranty_months": 12,
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _receive(client, headers, item_id, serial, **extra):
    payload = {"item_id": item_id, "serial": serial}
    payload.update(extra)
    response = client.post("/api/v1/serial-units", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _sell(client, headers, item_id, serial, customer_id=None):
    body = {
        "payment_method": "cash",
        "items": [{"item_id": item_id, "serial": serial, "quantity": 1}],
    }
    if customer_id:
        body["customer_id"] = customer_id
    billed = client.post("/api/v1/bills", headers=headers, json=body)
    assert billed.status_code == 201, billed.get_json()
    return billed.get_json()["data"]


def _customer(client, headers, name, phone):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": phone},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _audit_actions(client, headers, *, action=None):
    params = {"per_page": 100}
    if action:
        params["action"] = action
    response = client.get("/api/v1/audit-logs", headers=headers, query_string=params)
    assert response.status_code == 200, response.get_json()
    return [row["action"] for row in response.get_json()["data"]]


def test_restaurant_serial_vertical_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    for path in (
        "/api/v1/serial-units",
        "/api/v1/repairs",
        "/api/v1/installations",
        "/api/v1/mobile/sales",
    ):
        assert client.get(path, headers=headers).status_code == 403, path


def test_gate_module_matrix_mobile_vs_electronics(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "mobile")
    mobile = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in ("serial_imei", "warranty", "repair_service", "returns_exchange"):
        assert code in mobile
    assert "installation" not in mobile
    assert "order_channels" not in mobile
    assert "variants" not in mobile

    _switch(client, owner, "electronics")
    electronics = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in (
        "serial_imei",
        "warranty",
        "repair_service",
        "returns_exchange",
        "installation",
    ):
        assert code in electronics

    resto = login(client, "owner@hotelb.com", "Owner@12345")
    resto_modules = client.get("/api/v1/tenants/me/modules", headers=resto).get_json()["data"][
        "enabled_modules"
    ]
    assert "serial_imei" not in resto_modules
    assert "installation" not in resto_modules


def test_gate_imei_uniqueness_sell_and_block_resell(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "mobile")
    cat_id = _category(client, owner, "Gate-IMEI")
    phone = _item(client, owner, cat_id, "Gate Unique Phone")
    _receive(client, owner, phone["id"], "GATEIMEI34001")

    dup = client.post(
        "/api/v1/serial-units",
        headers=owner,
        json={"item_id": phone["id"], "serial": "gateimei34001"},
    )
    assert dup.status_code == 409, dup.get_json()

    bill = _sell(client, billing, phone["id"], "GATEIMEI34001")
    assert bill["items"][0]["serial_number"] == "GATEIMEI34001"

    resell = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": phone["id"], "serial": "GATEIMEI34001", "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert resell.status_code in {400, 409}, resell.get_json()


def test_gate_cross_tenant_imei_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a, "mobile")
    cat_id = _category(client, owner_a, "Gate-Iso-A")
    phone = _item(client, owner_a, cat_id, "Gate Iso Phone")
    unit = _receive(client, owner_a, phone["id"], "GATEISO34002")
    customer = _customer(client, owner_a, "Gate Iso Buyer", "9876340001")
    bill = _sell(client, owner_a, phone["id"], "GATEISO34002", customer_id=customer["id"])

    for path in (
        "/api/v1/serial-units",
        "/api/v1/repairs",
        "/api/v1/mobile/sales",
        "/api/v1/returns",
    ):
        assert client.get(path, headers=owner_b).status_code == 403, path

    _switch(client, owner_b, "mobile")
    listed = client.get(
        "/api/v1/serial-units",
        headers=owner_b,
        query_string={"q": "GATEISO34002"},
    )
    assert listed.status_code == 200, listed.get_json()
    assert listed.get_json()["data"] == []

    lookup = client.get(
        "/api/v1/serial-units/by-serial/GATEISO34002",
        headers=owner_b,
    )
    assert lookup.status_code == 404, lookup.get_json()

    history = client.get(
        "/api/v1/mobile/customer-history",
        headers=owner_b,
        query_string={"customer_id": customer["id"]},
    )
    assert history.status_code == 404, history.get_json()

    returns_lookup = client.get(
        "/api/v1/returns/lookup",
        headers=owner_b,
        query_string={"bill_number": bill["bill_number"]},
    )
    assert returns_lookup.status_code == 404, returns_lookup.get_json()

    # Same IMEI string allowed on another tenant
    cat_b = _category(client, owner_b, "Gate-Iso-B")
    phone_b = _item(client, owner_b, cat_b, "Gate Iso Phone B")
    other = _receive(client, owner_b, phone_b["id"], "GATEISO34002")
    assert other["serial"] == "GATEISO34002"
    assert other["id"] != unit["id"]


def test_gate_warranty_brand_model_and_mobile_report(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "mobile")
    cat_id = _category(client, owner, "Gate-Report")
    phone = _item(
        client,
        owner,
        cat_id,
        "Gate Report Phone",
        brand="Xiaomi",
        model_name="Redmi Gate",
        warranty_months=18,
    )
    _receive(client, owner, phone["id"], "GATEREPORT3403", warranty_months=6)
    bill = _sell(client, billing, phone["id"], "GATEREPORT3403")
    line = bill["items"][0]
    assert line["serial_number"] == "GATEREPORT3403"
    assert line.get("warranty_until")

    report = client.get("/api/v1/mobile/sales", headers=owner)
    assert report.status_code == 200, report.get_json()
    body = report.get_json()
    assert body["success"] is True
    data = body["data"]
    brands = {row["brand"] for row in data["by_brand"]}
    models = {row["model_name"] for row in data["by_model"]}
    assert "Xiaomi" in brands
    assert "Redmi Gate" in models
    assert "serial_stock_summary" in data


def test_gate_serial_return_quarantine_and_exchange(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "mobile")
    cat_id = _category(client, owner, "Gate-Return")
    phone = _item(client, owner, cat_id, "Gate Return Phone")
    old = _receive(client, owner, phone["id"], "GATERETURN3404")
    new = _receive(client, owner, phone["id"], "GATEEXCH34005")
    bill = _sell(client, billing, phone["id"], "GATERETURN3404")
    line = bill["items"][0]

    exchanged = client.post(
        "/api/v1/returns",
        headers=owner,
        json={
            "bill_id": bill["id"],
            "kind": "EXCHANGE",
            "reason": "DOA gate",
            "items": [
                {
                    "bill_item_id": line["id"],
                    "quantity": "1",
                    "exchange_serial_unit_id": new["id"],
                }
            ],
        },
    )
    assert exchanged.status_code == 201, exchanged.get_json()

    units = {
        row["serial"]: row["status"]
        for row in client.get(
            "/api/v1/serial-units",
            headers=owner,
            query_string={"item_id": phone["id"]},
        ).get_json()["data"]
    }
    assert units["GATERETURN3404"] == "QUARANTINE"
    assert units["GATEEXCH34005"] == "SOLD"

    bill_view = client.get(f"/api/v1/bills/{bill['id']}", headers=owner)
    assert bill_view.get_json()["data"]["items"][0]["serial_number"] == "GATEEXCH34005"
    assert old["id"] != new["id"]


def test_gate_repair_and_installation_permissions(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    manager = login(client, "manager@hotela.com", "Manager@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "electronics")
    cat_id = _category(client, owner, "Gate-Service")
    device = _item(client, owner, cat_id, "Gate AC", brand="LG", model_name="Split Gate")
    unit = _receive(client, owner, device["id"], "GATESVC34006")
    _sell(client, billing, device["id"], "GATESVC34006")

    assert client.get("/api/v1/repairs", headers=billing).status_code == 200
    assert client.get("/api/v1/installations", headers=billing).status_code == 200
    assert client.get("/api/v1/mobile/sales", headers=manager).status_code == 200
    assert client.get("/api/v1/mobile/sales", headers=billing).status_code == 403

    denied_repair = client.post(
        "/api/v1/repairs",
        headers=billing,
        json={"serial_unit_id": unit["id"], "issue_description": "No cooling"},
    )
    assert denied_repair.status_code == 403

    denied_install = client.post(
        "/api/v1/installations",
        headers=billing,
        json={
            "serial_unit_id": unit["id"],
            "scheduled_at": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT11:00:00"),
        },
    )
    assert denied_install.status_code == 403

    repair = client.post(
        "/api/v1/repairs",
        headers=manager,
        json={"serial_unit_id": unit["id"], "issue_description": "No cooling"},
    )
    assert repair.status_code == 201, repair.get_json()
    repair_id = repair.get_json()["data"]["id"]
    progressed = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers=manager,
        json={"status": "IN_PROGRESS"},
    )
    assert progressed.status_code == 200
    ready = client.patch(
        f"/api/v1/repairs/{repair_id}/status",
        headers=manager,
        json={"status": "READY"},
    )
    assert ready.status_code == 200

    install = client.post(
        "/api/v1/installations",
        headers=manager,
        json={
            "serial_unit_id": unit["id"],
            "scheduled_at": (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%dT15:00:00"),
            "install_address": "Gate Street 1",
        },
    )
    assert install.status_code == 201, install.get_json()
    assert client.get("/api/v1/installations", headers=owner).status_code == 200

    notifications = client.get("/api/v1/notifications", headers=owner)
    types = {row["type"] for row in notifications.get_json()["data"]}
    assert "REPAIR_READY" in types
    assert "INSTALLATION_SCHEDULED" in types


def test_gate_customer_history_and_audit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "mobile")
    cat_id = _category(client, owner, "Gate-History")
    phone = _item(client, owner, cat_id, "Gate History Phone", brand="Vivo", model_name="Y Gate")
    _receive(client, owner, phone["id"], "GATEHIST34007")
    customer = _customer(client, owner, "Gate History Buyer", "9876340007")
    bill = _sell(client, billing, phone["id"], "GATEHIST34007", customer_id=customer["id"])

    history = client.get(
        "/api/v1/mobile/customer-history",
        headers=owner,
        query_string={"customer_id": customer["id"]},
    )
    assert history.status_code == 200, history.get_json()
    payload = history.get_json()["data"]
    assert payload["customer"]["id"] == customer["id"]
    assert payload["bills"][0]["id"] == bill["id"]
    assert payload["bills"][0]["items"][0]["serial_number"] == "GATEHIST34007"

    actions = set(_audit_actions(client, owner))
    assert "RECEIVE_SERIAL" in actions or "SELL_SERIAL" in actions
    history_actions = set(_audit_actions(client, owner, action="VIEW_MOBILE_CUSTOMER_HISTORY"))
    assert "VIEW_MOBILE_CUSTOMER_HISTORY" in history_actions


def test_gate_api_contract_envelopes(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "electronics")
    for path in (
        "/api/v1/serial-units",
        "/api/v1/repairs",
        "/api/v1/installations",
        "/api/v1/mobile/sales",
        "/api/v1/returns",
    ):
        response = client.get(path, headers=owner)
        assert response.status_code == 200, (path, response.get_json())
        body = response.get_json()
        assert body["success"] is True
        assert "data" in body
        assert "error" in body


def test_gate_mobile_cannot_use_installations(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "mobile")
    assert client.get("/api/v1/installations", headers=owner).status_code == 403
