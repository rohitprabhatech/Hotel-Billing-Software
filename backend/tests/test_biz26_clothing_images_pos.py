"""Sprint BIZ-26 — clothing product images and variant stock POS."""

from io import BytesIO

from tests.conftest import login

PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _switch_clothing(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "clothing"},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()["data"]


def _category(client, headers, name="Wear"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "399",
        "gst_percentage": "0",
        "stock_quantity": "0",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_clothing_has_product_images_module(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    modules = client.get("/api/v1/tenants/me/modules", headers=headers).get_json()["data"][
        "enabled_modules"
    ]
    assert "product_images" in modules
    assert "variants" in modules


def test_restaurant_images_and_clothing_pos_forbidden(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    cat_id = _category(client, headers, "No Img")
    item = _item(client, headers, cat_id, "No Photo Shirt")
    denied = client.get(f"/api/v1/items/{item['id']}/images", headers=headers)
    assert denied.status_code == 403
    pos = client.get("/api/v1/clothing/pos-catalog", headers=headers)
    assert pos.status_code == 403


def test_image_url_and_upload_and_isolation(client):
    owner_a = login(client, "owner@hotela.com", "Owner@12345")
    owner_b = login(client, "owner@hotelb.com", "Owner@12345")
    _switch_clothing(client, owner_a)
    _switch_clothing(client, owner_b)
    cat_id = _category(client, owner_a)
    item = _item(client, owner_a, cat_id, "Photo Tee")

    bad = client.post(
        f"/api/v1/items/{item['id']}/images",
        headers=owner_a,
        json={"image_url": "javascript:alert(1)"},
    )
    assert bad.status_code == 400

    created = client.post(
        f"/api/v1/items/{item['id']}/images",
        headers=owner_a,
        json={"image_url": "https://cdn.example.com/tee.jpg", "is_primary": True},
    )
    assert created.status_code == 201, created.get_json()
    assert created.get_json()["data"]["is_primary"] is True

    uploaded = client.post(
        f"/api/v1/items/{item['id']}/images/upload",
        headers=owner_a,
        data={"file": (BytesIO(PNG_1X1), "swatch.png")},
        content_type="multipart/form-data",
    )
    assert uploaded.status_code == 201, uploaded.get_json()
    storage_url = uploaded.get_json()["data"]["image_url"]
    assert "/item-images/files/" in storage_url
    filename = storage_url.rsplit("/", 1)[-1]
    public = client.get(f"/api/v1/item-images/files/{filename}")
    assert public.status_code == 200

    listing = client.get(f"/api/v1/items/{item['id']}/images", headers=owner_a)
    assert listing.status_code == 200
    assert len(listing.get_json()["data"]) == 2

    other = client.get(f"/api/v1/items/{item['id']}/images", headers=owner_b)
    assert other.status_code in {403, 404}


def test_pos_catalog_variant_stock_and_selected_variant_sale(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    _switch_clothing(client, headers)
    cat_id = _category(client, headers)
    tee = _item(client, headers, cat_id, "Grid Tee")
    medium = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "M", "color": "Navy", "stock_quantity": "3"},
    ).get_json()["data"]
    large = client.post(
        f"/api/v1/items/{tee['id']}/variants",
        headers=headers,
        json={"size": "L", "color": "Navy", "stock_quantity": "5"},
    ).get_json()["data"]

    catalog = client.get("/api/v1/clothing/pos-catalog", headers=headers)
    assert catalog.status_code == 200, catalog.get_json()
    found = next(row for row in catalog.get_json()["data"]["items"] if row["id"] == tee["id"])
    assert found["tracks_variants"] is True
    assert "M" in found["sizes"] and "L" in found["sizes"]
    by_id = {row["id"]: row for row in found["variants"]}
    assert float(by_id[medium["id"]]["stock_quantity"]) == 3.0
    assert float(by_id[large["id"]]["stock_quantity"]) == 5.0

    oversell = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": tee["id"], "variant_id": medium["id"], "quantity": "9"}],
        },
    )
    assert oversell.status_code == 400

    billed = client.post(
        "/api/v1/bills",
        headers=headers,
        json={
            "payment_method": "cash",
            "items": [{"item_id": tee["id"], "variant_id": medium["id"], "quantity": "2"}],
        },
    )
    assert billed.status_code == 201, billed.get_json()
    assert billed.get_json()["data"]["items"][0]["variant_id"] == medium["id"]

    after = client.get(f"/api/v1/items/{tee['id']}/variants", headers=headers).get_json()["data"]
    stocks = {row["id"]: float(row["stock_quantity"]) for row in after}
    assert stocks[medium["id"]] == 1.0
    assert stocks[large["id"]] == 5.0
