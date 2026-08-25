"""Sprint BIZ-30 — warranty and accessories."""

from datetime import date

from tests.conftest import login


def _switch_mobile(client, headers):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": "mobile"},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Mobile"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "12000",
        "gst_percentage": "18",
        "tracks_serial": True,
        "warranty_months": 12,
        "stock_quantity": "0",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_warranty_on_serial_bill_and_accessories(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch_mobile(client, owner)
    cat_id = _category(client, owner)
    phone = _item(client, owner, cat_id, "Smartphone X", warranty_months=12)
    case = _item(
        client,
        owner,
        cat_id,
        "Phone Case",
        tracks_serial=False,
        stock_quantity="5",
        price="499",
        warranty_months=None,
    )

    linked = client.put(
        f"/api/v1/items/{phone['id']}/accessories",
        headers=owner,
        json={"accessory_item_ids": [case["id"]]},
    )
    assert linked.status_code == 200, linked.get_json()
    assert len(linked.get_json()["data"]) == 1

    client.post(
        "/api/v1/serial-units",
        headers=owner,
        json={"item_id": phone["id"], "serial": "SNWARRANTY01", "warranty_months": 6},
    )

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": phone["id"], "serial": "SNWARRANTY01", "quantity": 1}],
            "payment_method": "cash",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    line = bill.get_json()["data"]["items"][0]
    assert line["warranty_until"] is not None
    until = date.fromisoformat(line["warranty_until"])
    assert until > date.today()

    detail = client.get(f"/api/v1/bills/{bill.get_json()['data']['id']}", headers=billing)
    assert detail.status_code == 200
    assert detail.get_json()["data"]["items"][0]["warranty_until"] == line["warranty_until"]

    accessories = client.get(f"/api/v1/items/{phone['id']}/accessories", headers=owner)
    assert accessories.status_code == 200
    assert accessories.get_json()["data"][0]["id"] == case["id"]
