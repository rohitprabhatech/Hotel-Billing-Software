"""Sprint BIZ-51 — wholesale price lists and resolution order."""

from tests.conftest import login


def _switch_wholesale(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "wholesale"},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Wholesale"):
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


def _customer(client, headers, name="Trade Buyer", phone="9000000051"):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "91", "phone": phone},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_restaurant_price_lists_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    client.put(
        "/api/v1/tenants/me",
        headers=owner,
        json={"business_type": "hotel_restaurant"},
    )
    assert client.get("/api/v1/price-lists", headers=owner).status_code == 403
    assert client.get("/api/v1/wholesale/price-lists", headers=owner).status_code == 403


def test_wholesale_module_has_price_lists(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_wholesale(client, owner)
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    assert "price_lists" in modules
    assert "bulk_pricing" in modules


def test_price_resolution_customer_over_wholesale_over_retail(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_wholesale(client, owner)
    cat_id = _category(client, owner)
    widget = _item(client, owner, cat_id, "Trade Widget", price="100", stock_quantity="20")
    buyer = _customer(client, owner)

    wholesale = client.post(
        "/api/v1/price-lists",
        headers=owner,
        json={"name": "Default Wholesale", "list_type": "WHOLESALE", "is_default": True},
    )
    assert wholesale.status_code == 201, wholesale.get_json()
    wholesale_id = wholesale.get_json()["data"]["id"]

    customer_list = client.post(
        "/api/v1/wholesale/price-lists",
        headers=owner,
        json={"name": "VIP Distributors", "list_type": "WHOLESALE"},
    )
    assert customer_list.status_code == 201, customer_list.get_json()
    vip_id = customer_list.get_json()["data"]["id"]

    put_wholesale = client.put(
        f"/api/v1/price-lists/{wholesale_id}/items",
        headers=owner,
        json={"items": [{"item_id": widget["id"], "unit_price": "85"}]},
    )
    assert put_wholesale.status_code == 200, put_wholesale.get_json()

    put_vip = client.put(
        f"/api/v1/price-lists/{vip_id}/items",
        headers=owner,
        json={"items": [{"item_id": widget["id"], "unit_price": "75"}]},
    )
    assert put_vip.status_code == 200, put_vip.get_json()

    assigned = client.put(
        f"/api/v1/price-lists/customer-assignments/{buyer['id']}",
        headers=owner,
        json={"price_list_id": vip_id},
    )
    assert assigned.status_code == 200, assigned.get_json()

    walk_in = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": widget["id"], "quantity": "2"}],
        },
    )
    assert walk_in.status_code == 201, walk_in.get_json()
    assert walk_in.get_json()["data"]["items"][0]["unit_price"] == 85.0

    vip_bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "customer_id": buyer["id"],
            "items": [{"item_id": widget["id"], "quantity": "2"}],
        },
    )
    assert vip_bill.status_code == 201, vip_bill.get_json()
    assert vip_bill.get_json()["data"]["items"][0]["unit_price"] == 75.0


def test_bulk_tier_applies_when_no_list_price(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_wholesale(client, owner)
    cat_id = _category(client, owner)
    rice = _item(client, owner, cat_id, "Bulk Rice", price="100", stock_quantity="100")

    tiers = client.put(
        f"/api/v1/items/{rice['id']}/price-tiers",
        headers=owner,
        json={"tiers": [{"min_quantity": "10", "unit_price": "80"}]},
    )
    assert tiers.status_code == 200, tiers.get_json()

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": rice["id"], "quantity": "10"}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    assert bill.get_json()["data"]["items"][0]["unit_price"] == 80.0


def test_pos_catalog_includes_list_price_for_customer(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch_wholesale(client, owner)
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, "POS Widget", price="100")
    buyer = _customer(client, owner, phone="9000000052")

    wholesale = client.post(
        "/api/v1/price-lists",
        headers=owner,
        json={"name": "POS Wholesale", "is_default": True},
    )
    wid = wholesale.get_json()["data"]["id"]
    client.put(
        f"/api/v1/price-lists/{wid}/items",
        headers=owner,
        json={"items": [{"item_id": item["id"], "unit_price": "88"}]},
    )
    vip = client.post(
        "/api/v1/price-lists",
        headers=owner,
        json={"name": "POS VIP"},
    )
    vid = vip.get_json()["data"]["id"]
    client.put(
        f"/api/v1/price-lists/{vid}/items",
        headers=owner,
        json={"items": [{"item_id": item["id"], "unit_price": "77"}]},
    )
    client.put(
        f"/api/v1/price-lists/customer-assignments/{buyer['id']}",
        headers=owner,
        json={"price_list_id": vid},
    )

    default_catalog = client.get("/api/v1/grocery/pos-catalog", headers=owner)
    assert default_catalog.status_code == 200, default_catalog.get_json()
    row = next(i for i in default_catalog.get_json()["data"]["items"] if i["id"] == item["id"])
    assert row["base_price"] == 88.0

    vip_catalog = client.get(
        "/api/v1/grocery/pos-catalog",
        headers=owner,
        query_string={"customer_id": buyer["id"]},
    )
    assert vip_catalog.status_code == 200, vip_catalog.get_json()
    row_vip = next(i for i in vip_catalog.get_json()["data"]["items"] if i["id"] == item["id"])
    assert row_vip["base_price"] == 77.0


def test_billing_cannot_create_price_list(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_wholesale(client, owner)

    listed = client.get("/api/v1/price-lists", headers=billing)
    assert listed.status_code == 200, listed.get_json()

    denied = client.post(
        "/api/v1/price-lists",
        headers=billing,
        json={"name": "Blocked"},
    )
    assert denied.status_code == 403, denied.get_json()


def test_price_list_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_wholesale(client, owner_a)
    _switch_wholesale(client, owner_b)

    created = client.post(
        "/api/v1/price-lists",
        headers=owner_a,
        json={"name": "Tenant A List"},
    )
    assert created.status_code == 201, created.get_json()
    lid = created.get_json()["data"]["id"]

    foreign = client.get(f"/api/v1/wholesale/price-lists/{lid}", headers=owner_b)
    assert foreign.status_code == 404, foreign.get_json()
