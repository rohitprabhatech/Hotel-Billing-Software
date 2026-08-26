"""Sprint BIZ-50 — furniture quotations via shared module (BIZ-36 reuse)."""

from tests.conftest import login


def _switch(client, headers, business_type="furniture"):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Living"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _sofa(client, headers, category_id, name="Gate Sofa", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "28000",
        "gst_percentage": "18",
        "stock_quantity": "2",
        "uom": "pcs",
        "dimension_length": "84",
        "dimension_width": "36",
        "dimension_height": "32",
        "material": "Teak",
        "color": "Natural",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_restaurant_furniture_quotations_forbidden(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/quotations", headers=owner).status_code == 403
    assert client.get("/api/v1/furniture/quotations", headers=owner).status_code == 403


def test_furniture_quotation_alias_create_and_convert(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    sofa = _sofa(client, owner, cat_id)

    created = client.post(
        "/api/v1/furniture/quotations",
        headers=owner,
        json={
            "customer_name": "Home Buyer",
            "notes": "Living room set",
            "items": [{"item_id": sofa["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    quote = created.get_json()["data"]
    assert quote["quotation_number"].startswith("QT-")
    assert quote["status"] == "DRAFT"
    assert len(quote["items"]) == 1

    alias_list = client.get("/api/v1/furniture/quotations", headers=billing)
    assert alias_list.status_code == 200, alias_list.get_json()
    assert any(row["id"] == quote["id"] for row in alias_list.get_json()["data"])

    denied = client.post(
        f"/api/v1/furniture/quotations/{quote['id']}/convert",
        headers=billing,
        json={"payment_method": "cash"},
    )
    assert denied.status_code == 403, denied.get_json()

    converted = client.post(
        f"/api/v1/quotations/{quote['id']}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted.status_code == 200, converted.get_json()
    body = converted.get_json()["data"]
    assert body["quotation"]["status"] == "CONVERTED"
    assert body["bill"]["id"] == body["quotation"]["bill_id"]

    stock = client.get(f"/api/v1/items/{sofa['id']}", headers=owner).get_json()["data"]
    assert stock["stock_quantity"] == 1.0


def test_furniture_quotation_cross_tenant_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch(client, owner_a)
    _switch(client, owner_b)
    cat_id = _category(client, owner_a)
    sofa = _sofa(client, owner_a, cat_id, name="Iso Sofa")
    created = client.post(
        "/api/v1/quotations",
        headers=owner_a,
        json={
            "customer_name": "Tenant A",
            "items": [{"item_id": sofa["id"], "quantity": "1"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    qid = created.get_json()["data"]["id"]

    foreign = client.get(f"/api/v1/furniture/quotations/{qid}", headers=owner_b)
    assert foreign.status_code == 404, foreign.get_json()
