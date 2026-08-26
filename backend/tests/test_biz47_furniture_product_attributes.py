"""Sprint BIZ-47 — furniture product attributes (dimensions / material / color)."""

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


def _sofa(client, headers, category_id, name="Teak Sofa", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "25000",
        "gst_percentage": "18",
        "stock_quantity": "3",
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


def test_furniture_module_flags(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
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
    assert "book_metadata" not in modules


def test_furniture_attributes_create_and_update(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    sofa = _sofa(client, owner, cat_id)
    assert sofa["dimension_length"] == 84.0
    assert sofa["dimension_width"] == 36.0
    assert sofa["dimension_height"] == 32.0
    assert sofa["material"] == "Teak"
    assert sofa["color"] == "Natural"

    updated = client.put(
        f"/api/v1/items/{sofa['id']}",
        headers=owner,
        json={
            "dimension_length": "90",
            "material": "Rosewood",
            "color": "Walnut",
        },
    )
    assert updated.status_code == 200, updated.get_json()
    body = updated.get_json()["data"]
    assert body["dimension_length"] == 90.0
    assert body["dimension_width"] == 36.0
    assert body["material"] == "Rosewood"
    assert body["color"] == "Walnut"


def test_furniture_search_by_material_and_color(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner, "Beds")
    bed = _sofa(
        client,
        owner,
        cat_id,
        name="Queen Bed",
        material="Plywood",
        color="White",
        dimension_length="60",
        dimension_width="80",
        dimension_height="40",
    )

    by_mat = client.get("/api/v1/items", headers=owner, query_string={"q": "Plywood"})
    assert by_mat.status_code == 200, by_mat.get_json()
    assert any(row["id"] == bed["id"] for row in by_mat.get_json()["data"])

    by_color = client.get("/api/v1/items", headers=owner, query_string={"q": "White"})
    assert by_color.status_code == 200, by_color.get_json()
    assert any(row["id"] == bed["id"] for row in by_color.get_json()["data"])


def test_furniture_negative_dimension_rejected(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner, "Tables")
    bad = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Bad Table",
            "category_id": cat_id,
            "price": "5000",
            "gst_percentage": "18",
            "dimension_length": "-1",
            "uom": "pcs",
        },
    )
    assert bad.status_code == 400, bad.get_json()


def test_furniture_attributes_not_on_restaurant_modules(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    assert "furniture_attributes" not in modules
