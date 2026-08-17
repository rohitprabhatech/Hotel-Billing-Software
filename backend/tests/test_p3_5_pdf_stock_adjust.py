"""P3-5: bill PDF download + stock adjust."""

from tests.conftest import login


def test_download_bill_pdf_matches_saved_total(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    cat = client.post(
        "/api/v1/categories", headers=owner, json={"name": "PDF Cat"}
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "PDF Rice",
            "category_id": cat,
            "price": 100,
            "gst_percentage": 0,
            "stock_quantity": None,
        },
    ).get_json()["data"]

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": 2}],
        },
    ).get_json()["data"]
    assert bill["grand_total"] == 200.0

    pdf = client.get(f"/api/v1/bills/{bill['id']}/pdf", headers=billing)
    assert pdf.status_code == 200
    assert pdf.mimetype == "application/pdf"
    assert pdf.data[:4] == b"%PDF"
    assert len(pdf.data) > 100
    # Bill financial total unchanged (PDF is a view of saved data, not a recalculation API)
    again = client.get(f"/api/v1/bills/{bill['id']}", headers=billing).get_json()["data"]
    assert again["grand_total"] == 200.0
    assert again["bill_number"] == bill["bill_number"]


def test_adjust_stock_delta_and_reject_negative(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    cat = client.post(
        "/api/v1/categories", headers=owner, json={"name": "Adj Cat"}
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Adjust Item",
            "category_id": cat,
            "price": 50,
            "gst_percentage": 0,
            "stock_quantity": 10,
            "minimum_stock_level": 3,
        },
    ).get_json()["data"]

    up = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": 5, "reason": "Restock"},
    )
    assert up.status_code == 200, up.get_json()
    assert up.get_json()["data"]["stock_quantity"] == 15.0

    down = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": -4, "reason": "Damage"},
    )
    assert down.status_code == 200
    assert down.get_json()["data"]["stock_quantity"] == 11.0

    bad = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": -50},
    )
    assert bad.status_code == 400
    still = client.get(f"/api/v1/items/{item['id']}", headers=owner).get_json()["data"]
    assert still["stock_quantity"] == 11.0


def test_adjust_stock_untracked_rejected(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    cat = client.post(
        "/api/v1/categories", headers=owner, json={"name": "Untracked Cat"}
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Service Fee",
            "category_id": cat,
            "price": 10,
            "gst_percentage": 0,
            "stock_quantity": None,
        },
    ).get_json()["data"]

    res = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": 1},
    )
    assert res.status_code == 400
    assert "does not track stock" in res.get_json()["error"]["message"].lower()
