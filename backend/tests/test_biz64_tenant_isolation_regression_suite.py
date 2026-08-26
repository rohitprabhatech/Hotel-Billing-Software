"""Sprint BIZ-64 — tenant isolation regression suite.

Parametrized IDOR probes across industry entities. Attacker is Billing User
of the other tenant (tenant B) attempting cross-tenant reads/writes.

Run (CI / local):
  pytest tests/test_biz64_tenant_isolation_regression_suite.py -q
  pytest -m isolation -q
"""

from datetime import datetime, timedelta

import pytest

from tests.conftest import login

pytestmark = pytest.mark.isolation


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "0",
        "stock_quantity": "50",
        "uom": "pcs",
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


def _assert_no_cross_tenant(client, attacker, method, path, *, json=None, allow=(404,)):
    if method == "GET":
        response = client.get(path, headers=attacker)
    elif method == "PATCH":
        response = client.patch(path, headers=attacker, json=json or {})
    elif method == "POST":
        response = client.post(path, headers=attacker, json=json or {})
    elif method == "DELETE":
        response = client.delete(path, headers=attacker)
    else:
        raise AssertionError(f"unsupported method {method}")
    assert response.status_code in allow, (method, path, response.status_code, response.get_json())
    return response


def _assert_owner_ok(client, owner, path):
    response = client.get(path, headers=owner)
    assert response.status_code == 200, (path, response.get_json())


# (cluster_id, business_type) — each cluster seeds victim resources then probes.
ISOLATION_CLUSTERS = (
    "fb_kot",
    "mobile_repair",
    "electronics_install",
    "hardware_docs",
    "bakery_custom_prod",
    "furniture_delivery",
    "wholesale_trade",
    "travel_agency",
)


@pytest.mark.parametrize("cluster", ISOLATION_CLUSTERS)
def test_industry_cluster_cross_tenant_idor(client, cluster):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    billing_a = login(client, "billing@hotela.com", "Billing@12345")
    manager_a = login(client, "manager@hotela.com", "Manager@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    # Peer-tenant Owner for permission-parity IDOR; Billing attacker covered via billing_probes.
    attacker = owner_b
    billing_attacker = login(client, "billing@hotelb.com", "Billing@12345")

    probes = []
    billing_probes = []
    if cluster == "fb_kot":
        _switch(client, owner_a, "hotel_restaurant")
        _switch(client, owner_b, "hotel_restaurant")
        cat = _category(client, owner_a, "Iso KOT Cat")
        item = _item(client, owner_a, cat, "Iso KOT Item")
        order = client.post(
            "/api/v1/orders",
            headers=owner_a,
            json={
                "channel": "takeaway",
                "customer_name": "Iso Guest",
                "items": [{"item_id": item["id"], "quantity": "1"}],
            },
        ).get_json()["data"]
        kot = client.post(
            f"/api/v1/orders/{order['id']}/kot", headers=owner_a
        ).get_json()["data"]
        probes = [
            ("GET", f"/api/v1/kots/{kot['id']}", None, (404,)),
            ("GET", f"/api/v1/orders/{order['id']}", None, (404,)),
            ("PATCH", f"/api/v1/kots/{kot['id']}/status", {"status": "ready"}, (404, 403)),
        ]
        billing_probes = [
            ("GET", f"/api/v1/kots/{kot['id']}", None, (404, 403)),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/kots/{kot['id']}")

    elif cluster == "mobile_repair":
        _switch(client, owner_a, "mobile")
        _switch(client, owner_b, "mobile")
        cat = _category(client, owner_a, "Iso Mobile")
        phone = _item(
            client,
            owner_a,
            cat,
            "Iso Phone",
            tracks_serial=True,
            stock_quantity="0",
            price="15000",
            gst_percentage="18",
        )
        unit = client.post(
            "/api/v1/serial-units",
            headers=owner_a,
            json={"item_id": phone["id"], "serial": "SNISO6401"},
        ).get_json()["data"]
        client.post(
            "/api/v1/bills",
            headers=billing_a,
            json={
                "items": [{"item_id": phone["id"], "serial": "SNISO6401", "quantity": 1}],
                "payment_method": "cash",
            },
        )
        repair = client.post(
            "/api/v1/repairs",
            headers=owner_a,
            json={
                "serial_unit_id": unit["id"],
                "issue_description": "Isolation probe",
                "customer_name": "Iso Ravi",
            },
        ).get_json()["data"]
        probes = [
            ("GET", f"/api/v1/repairs/{repair['id']}", None, (404,)),
            ("GET", "/api/v1/serial-units/by-serial/SNISO6401", None, (404,)),
            ("PATCH", f"/api/v1/repairs/{repair['id']}/status", {"status": "READY"}, (404, 403)),
        ]
        billing_probes = [
            ("GET", f"/api/v1/repairs/{repair['id']}", None, (404, 403)),
            ("GET", "/api/v1/serial-units/by-serial/SNISO6401", None, (404, 403)),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/repairs/{repair['id']}")

    elif cluster == "electronics_install":
        _switch(client, owner_a, "electronics")
        _switch(client, owner_b, "electronics")
        cat = _category(client, owner_a, "Iso Elec")
        ac = _item(
            client,
            owner_a,
            cat,
            "Iso AC",
            tracks_serial=True,
            stock_quantity="0",
            price="25000",
            gst_percentage="18",
        )
        unit = client.post(
            "/api/v1/serial-units",
            headers=owner_a,
            json={"item_id": ac["id"], "serial": "SNISO6402"},
        ).get_json()["data"]
        client.post(
            "/api/v1/bills",
            headers=billing_a,
            json={
                "items": [{"item_id": ac["id"], "serial": "SNISO6402", "quantity": 1}],
                "payment_method": "cash",
            },
        )
        install = client.post(
            "/api/v1/installations",
            headers=owner_a,
            json={
                "serial_unit_id": unit["id"],
                "scheduled_at": (datetime.utcnow() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT10:00:00"
                ),
                "customer_name": "Iso Install",
            },
        ).get_json()["data"]
        probes = [
            ("GET", f"/api/v1/installations/{install['id']}", None, (404,)),
            (
                "PATCH",
                f"/api/v1/installations/{install['id']}/status",
                {"status": "COMPLETED"},
                (404, 403),
            ),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/installations/{install['id']}")

    elif cluster == "hardware_docs":
        _switch(client, owner_a, "building_material")
        _switch(client, owner_b, "building_material")
        cat = _category(client, owner_a, "Iso HW")
        pipe = _item(client, owner_a, cat, "Iso Pipe", price="450", uom="m")
        quote = client.post(
            "/api/v1/quotations",
            headers=owner_a,
            json={
                "customer_name": "Iso Quote",
                "items": [{"item_id": pipe["id"], "quantity": "2"}],
            },
        ).get_json()["data"]
        challan = client.post(
            "/api/v1/challans",
            headers=owner_a,
            json={
                "customer_name": "Iso Challan",
                "items": [{"item_id": pipe["id"], "quantity": "1"}],
            },
        ).get_json()["data"]
        wh_resp = client.post(
            "/api/v1/warehouses",
            headers=owner_a,
            json={"code": "ISO64", "name": "Iso Yard"},
        )
        assert wh_resp.status_code == 201, wh_resp.get_json()
        wh = wh_resp.get_json()["data"]
        probes = [
            ("GET", f"/api/v1/quotations/{quote['id']}", None, (404,)),
            ("GET", f"/api/v1/challans/{challan['id']}", None, (404,)),
            ("PATCH", f"/api/v1/warehouses/{wh['id']}", {"name": "Hijack"}, (404, 403)),
        ]
        billing_probes = [
            ("GET", f"/api/v1/quotations/{quote['id']}", None, (404, 403)),
            ("GET", f"/api/v1/challans/{challan['id']}", None, (404, 403)),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/quotations/{quote['id']}")
        _assert_owner_ok(client, owner_a, f"/api/v1/challans/{challan['id']}")

    elif cluster == "bakery_custom_prod":
        _switch(client, owner_a, "bakery_sweet")
        _switch(client, owner_b, "bakery_sweet")
        cat = _category(client, owner_a, "Iso Bake")
        cake = _item(client, owner_a, cat, "Iso Cake", stock="5", price="400")
        flour = _item(client, owner_a, cat, "Iso Flour", stock="100")
        recipe = client.post(
            "/api/v1/recipes",
            headers=owner_a,
            json={
                "menu_item_id": cake["id"],
                "name": "Iso BOM",
                "yield_quantity": 1,
                "ingredients": [{"ingredient_item_id": flour["id"], "quantity": "2"}],
            },
        ).get_json()["data"]
        run = client.post(
            "/api/v1/productions",
            headers=owner_a,
            json={"recipe_id": recipe["id"], "quantity": "1"},
        ).get_json()["data"]
        custom = client.post(
            "/api/v1/custom-orders",
            headers=billing_a,
            json={
                "order_type": "bakery",
                "title": "Iso Birthday",
                "total_amount": "2000",
                "advance_amount": "500",
                "customer_name": "Iso Cake Cust",
            },
        ).get_json()["data"]
        probes = [
            ("GET", f"/api/v1/productions/{run['id']}", None, (404,)),
            ("GET", f"/api/v1/custom-orders/{custom['id']}", None, (404,)),
            ("GET", f"/api/v1/recipes/{recipe['id']}", None, (404,)),
            (
                "PATCH",
                f"/api/v1/custom-orders/{custom['id']}/status",
                {"status": "CONFIRMED"},
                (404, 403),
            ),
        ]
        billing_probes = [
            ("GET", f"/api/v1/custom-orders/{custom['id']}", None, (404, 403)),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/custom-orders/{custom['id']}")
        _assert_owner_ok(client, owner_a, f"/api/v1/productions/{run['id']}")

    elif cluster == "furniture_delivery":
        _switch(client, owner_a, "furniture")
        _switch(client, owner_b, "furniture")
        delivery_at = (datetime.utcnow() + timedelta(days=5)).isoformat()
        custom = client.post(
            "/api/v1/furniture/custom-orders",
            headers=billing_a,
            json={
                "title": "Iso Wardrobe",
                "customer_name": "Iso Furniture",
                "total_amount": "35000",
                "advance_amount": "10000",
                "delivery_at": delivery_at,
            },
        ).get_json()["data"]
        oid = custom["id"]
        for status in ("CONFIRMED", "IN_PRODUCTION", "READY"):
            assert (
                client.patch(
                    f"/api/v1/custom-orders/{oid}/status",
                    headers=manager_a,
                    json={"status": status},
                ).status_code
                == 200
            )
        delivery = client.post(
            "/api/v1/deliveries",
            headers=owner_a,
            json={
                "custom_order_id": oid,
                "delivery_address": "Iso Address",
                "scheduled_at": (datetime.utcnow() + timedelta(days=2)).strftime(
                    "%Y-%m-%dT14:00:00"
                ),
            },
        ).get_json()["data"]
        probes = [
            ("GET", f"/api/v1/custom-orders/{oid}", None, (404,)),
            ("GET", f"/api/v1/deliveries/{delivery['id']}", None, (404,)),
            (
                "PATCH",
                f"/api/v1/deliveries/{delivery['id']}/status",
                {"status": "OUT_FOR_DELIVERY"},
                (404, 403),
            ),
        ]
        billing_probes = [
            ("GET", f"/api/v1/deliveries/{delivery['id']}", None, (404, 403)),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/deliveries/{delivery['id']}")

    elif cluster == "wholesale_trade":
        _switch(client, owner_a, "wholesale")
        _switch(client, owner_b, "wholesale")
        cat = _category(client, owner_a, "Iso WH")
        item = _item(client, owner_a, cat, "Iso Carton", stock_quantity="40")
        buyer = _customer(client, owner_a, "Iso Dealer", "9000000064")
        vendor = _supplier(client, owner_a, "Iso Vendor")
        pl = client.post(
            "/api/v1/price-lists",
            headers=owner_a,
            json={"name": "Iso List", "list_type": "WHOLESALE"},
        ).get_json()["data"]
        so = client.post(
            "/api/v1/sales-orders",
            headers=owner_a,
            json={
                "customer_id": buyer["id"],
                "items": [{"item_id": item["id"], "quantity": "1"}],
            },
        ).get_json()["data"]
        po = client.post(
            "/api/v1/purchase-orders",
            headers=owner_a,
            json={
                "supplier_id": vendor["id"],
                "items": [{"item_id": item["id"], "quantity": "2", "unit_cost": "50"}],
            },
        ).get_json()["data"]
        probes = [
            ("GET", f"/api/v1/price-lists/{pl['id']}", None, (404,)),
            ("GET", f"/api/v1/sales-orders/{so['id']}", None, (404,)),
            ("GET", f"/api/v1/purchase-orders/{po['id']}", None, (404,)),
            ("GET", f"/api/v1/customers/{buyer['id']}", None, (404,)),
        ]
        billing_probes = [
            ("GET", f"/api/v1/customers/{buyer['id']}", None, (404,)),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/sales-orders/{so['id']}")

    elif cluster == "travel_agency":
        _switch(client, owner_a, "travel_agency")
        _switch(client, owner_b, "travel_agency")
        pkg = client.post(
            "/api/v1/travel/packages",
            headers=owner_a,
            json={
                "code": "ISO64",
                "name": "Iso Trip",
                "destination": "Goa",
                "duration_days": 3,
                "base_price": "5000",
                "gst_percentage": "0",
            },
        ).get_json()["data"]
        booking = client.post(
            "/api/v1/travel/bookings",
            headers=owner_a,
            json={
                "package_id": pkg["id"],
                "customer_name": "Iso Traveler",
                "pax_count": 1,
            },
        ).get_json()["data"]
        bid = booking["id"]
        itinerary = client.post(
            f"/api/v1/travel/bookings/{bid}/itinerary",
            headers=owner_a,
            json={"item_type": "HOTEL", "title": "Iso Hotel", "day_number": 1},
        ).get_json()["data"]
        agent_resp = client.post(
            "/api/v1/travel/agents",
            headers=owner_a,
            json={"code": "ISOAG", "name": "Iso Agent", "commission_percent": "10"},
        )
        assert agent_resp.status_code == 201, agent_resp.get_json()
        agent = agent_resp.get_json()["data"]
        probes = [
            ("GET", f"/api/v1/travel/packages/{pkg['id']}", None, (404,)),
            ("GET", f"/api/v1/travel/bookings/{bid}", None, (404,)),
            ("GET", f"/api/v1/travel/bookings/{bid}/itinerary", None, (404,)),
            ("GET", f"/api/v1/travel/agents/{agent['id']}", None, (404,)),
            (
                "PATCH",
                f"/api/v1/travel/bookings/{bid}/itinerary/{itinerary['id']}",
                {"title": "Hijack"},
                (404, 403),
            ),
        ]
        billing_probes = [
            ("GET", f"/api/v1/travel/bookings/{bid}", None, (404, 403)),
        ]
        _assert_owner_ok(client, owner_a, f"/api/v1/travel/bookings/{bid}")
    else:
        raise AssertionError(f"unknown cluster {cluster}")

    for method, path, body, allow in probes:
        _assert_no_cross_tenant(
            client, attacker, method, path, json=body, allow=allow
        )

    for method, path, body, allow in billing_probes:
        _assert_no_cross_tenant(
            client, billing_attacker, method, path, json=body, allow=allow
        )


def test_audit_logs_are_tenant_scoped(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    attacker = login(client, "billing@hotelb.com", "Billing@12345")
    _switch(client, owner_a, "travel_agency")
    _switch(client, owner_b, "travel_agency")

    pkg = client.post(
        "/api/v1/travel/packages",
        headers=owner_a,
        json={
            "code": "AUD64",
            "name": "Audit Trip",
            "destination": "Pune",
            "duration_days": 2,
            "base_price": "3000",
            "gst_percentage": "0",
        },
    ).get_json()["data"]

    logs_a = client.get(
        "/api/v1/audit-logs",
        headers=owner_a,
        query_string={"per_page": 100},
    )
    assert logs_a.status_code == 200
    ids_a = {row["entity_id"] for row in logs_a.get_json()["data"]}
    assert pkg["id"] in ids_a

    logs_b = client.get(
        "/api/v1/audit-logs",
        headers=owner_b,
        query_string={"per_page": 100},
    )
    assert logs_b.status_code == 200
    ids_b = {row["entity_id"] for row in logs_b.get_json()["data"]}
    assert pkg["id"] not in ids_b

    # Billing attacker on B still cannot see A's entity via direct GET
    _assert_no_cross_tenant(
        client, attacker, "GET", f"/api/v1/travel/packages/{pkg['id']}", allow=(404,)
    )


def test_client_tenant_id_body_cannot_hijack_ownership(client):
    """tenant_id in request body must be ignored (JWT context wins)."""
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    attacker = login(client, "billing@hotelb.com", "Billing@12345")
    tenant_b_id = client.get("/api/v1/tenants/me", headers=owner_b).get_json()["data"]["id"]

    created = client.post(
        "/api/v1/customers",
        headers=owner_a,
        json={
            "name": "Hijack Target",
            "phone_country_code": "91",
            "phone": "9000000065",
            "tenant_id": tenant_b_id,
        },
    )
    assert created.status_code == 201, created.get_json()
    customer_id = created.get_json()["data"]["id"]

    assert client.get(f"/api/v1/customers/{customer_id}", headers=owner_a).status_code == 200
    assert client.get(f"/api/v1/customers/{customer_id}", headers=owner_b).status_code == 404
    assert client.get(f"/api/v1/customers/{customer_id}", headers=attacker).status_code == 404
