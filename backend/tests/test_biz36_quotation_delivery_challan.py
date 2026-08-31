"""Sprint BIZ-36 — quotations and delivery challans convertible to bills."""

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Cement"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "500",
        "gst_percentage": "18",
        "stock_quantity": "100",
        "uom": "bag",
    }
    # bag may not be allowed — use pcs
    payload["uom"] = "pcs"
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_quotation_convert_preserves_lines(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner)
    cement = _item(client, owner, cat_id, "OPC 53", price="350", stock_quantity="80")
    sand = _item(client, owner, cat_id, "River Sand", price="45", uom="kg", stock_quantity="500")

    created = client.post(
        "/api/v1/quotations",
        headers=owner,
        json={
            "customer_name": "Site Contractor",
            "discount": "0",
            "items": [
                {"item_id": cement["id"], "quantity": "10"},
                {"item_id": sand["id"], "quantity": "25"},
            ],
        },
    )
    assert created.status_code == 201, created.get_json()
    quote = created.get_json()["data"]
    assert quote["quotation_number"].startswith("QT-")
    assert quote["status"] == "DRAFT"
    assert len(quote["items"]) == 2
    assert quote["items"][0]["quantity"] == 10.0
    assert quote["items"][1]["quantity"] == 25.0

    billing = login(client, "billing@hotela.com", "Billing@12345")
    denied = client.post(f"/api/v1/quotations/{quote['id']}/convert", headers=billing, json={})
    assert denied.status_code == 403, denied.get_json()

    converted = client.post(
        f"/api/v1/quotations/{quote['id']}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted.status_code == 200, converted.get_json()
    body = converted.get_json()["data"]
    assert body["quotation"]["status"] == "CONVERTED"
    assert body["quotation"]["bill_id"] == body["bill"]["id"]
    bill_items = body["bill"]["items"]
    bill_by_item = {line["item_id"]: line for line in bill_items}
    assert bill_by_item[cement["id"]]["quantity"] == 10.0
    assert bill_by_item[sand["id"]]["quantity"] == 25.0


def test_challan_pdf_and_convert(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hardware")
    cat_id = _category(client, owner, "Pipes")
    pipe = _item(client, owner, cat_id, "GI Pipe", price="450", uom="m", stock_quantity="100")

    created = client.post(
        "/api/v1/challans",
        headers=owner,
        json={
            "customer_name": "Builder Co",
            "delivery_address": "Plot 12, MIDC",
            "vehicle_number": "MH12AB1234",
            "items": [{"item_id": pipe["id"], "quantity": "10"}],
        },
    )
    assert created.status_code == 201, created.get_json()
    challan = created.get_json()["data"]
    assert challan["challan_number"].startswith("DC-")
    assert challan["items"][0]["quantity"] == 10.0

    pdf = client.get(f"/api/v1/challans/{challan['id']}/pdf", headers=owner)
    assert pdf.status_code == 200, pdf.data[:200]
    assert pdf.headers.get("Content-Type", "").startswith("application/pdf")
    assert pdf.data[:4] == b"%PDF"

    converted = client.post(
        f"/api/v1/challans/{challan['id']}/convert",
        headers=owner,
        json={"payment_method": "cash"},
    )
    assert converted.status_code == 200, converted.get_json()
    body = converted.get_json()["data"]
    assert body["challan"]["status"] == "CONVERTED"
    assert body["bill"]["items"][0]["item_id"] == pipe["id"]
    assert body["bill"]["items"][0]["quantity"] == 10.0
    assert body["bill"]["reference"] == challan["challan_number"] or body["bill"].get(
        "table_number"
    ) == challan["challan_number"]


def test_restaurant_denied_documents(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/quotations", headers=owner).status_code == 403
    assert client.get("/api/v1/challans", headers=owner).status_code == 403


def test_wholesale_reuses_quotation_module(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner, "Bulk")
    item = _item(client, owner, cat_id, "Carton Pack", price="120", stock_quantity="40")
    created = client.post(
        "/api/v1/quotations",
        headers=owner,
        json={"items": [{"item_id": item["id"], "quantity": "2"}]},
    )
    assert created.status_code == 201, created.get_json()
    listing = client.get("/api/v1/quotations", headers=owner)
    assert listing.status_code == 200, listing.get_json()
    assert listing.get_json()["meta"]["total"] >= 1
