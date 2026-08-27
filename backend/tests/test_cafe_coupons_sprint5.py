"""Sprint 5: Cafe coupons CRUD + settle apply; hotel blocked."""

from decimal import Decimal

from tests.conftest import login


def _category(client, headers, name):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name, *, is_menu=True, stock="100", price="100"):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": price,
        "gst_percentage": "5",
        "stock_quantity": stock,
        "is_menu": is_menu,
    }
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_cafe_coupon_crud_and_preview(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")

    create = client.post(
        "/api/v1/coupons",
        headers=headers,
        json={
            "code": "TEA10",
            "name": "10% off",
            "discount_type": "percent",
            "discount_value": 10,
            "min_order_amount": 0,
            "usage_limit": 100,
        },
    )
    assert create.status_code == 201, create.get_json()
    coupon = create.get_json()["data"]
    assert coupon["code"] == "TEA10"
    assert coupon["discount_type"] == "percent"

    listed = client.get("/api/v1/coupons", headers=headers)
    assert listed.status_code == 200
    assert any(c["code"] == "TEA10" for c in listed.get_json()["data"])

    preview = client.post(
        "/api/v1/coupons/preview",
        headers=headers,
        json={"code": "tea10", "subtotal": 200},
    )
    assert preview.status_code == 200, preview.get_json()
    body = preview.get_json()["data"]
    assert Decimal(str(body["discount_amount"])) == Decimal("20.00")
    assert Decimal(str(body["subtotal"])) == Decimal("200.00")


def test_cafe_settle_applies_coupon(client):
    headers = login(client, "owner@hotelb.com", "Owner@12345")
    cat_id = _category(client, headers, "Coupon Settle Cat")
    item = _item(client, headers, cat_id, "Coupon Tea", price="100")

    created = client.post(
        "/api/v1/coupons",
        headers=headers,
        json={
            "code": "FLAT50",
            "name": "Flat 50",
            "discount_type": "amount",
            "discount_value": 50,
        },
    )
    assert created.status_code == 201, created.get_json()

    order_res = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "channel": "takeaway",
            "items": [{"item_id": item["id"], "quantity": "2"}],
        },
    )
    assert order_res.status_code == 201, order_res.get_json()
    order_id = order_res.get_json()["data"]["id"]

    settle = client.post(
        f"/api/v1/orders/{order_id}/settle",
        headers=headers,
        json={
            "payment_method": "cash",
            "discount": 0,
            "coupon_code": "FLAT50",
        },
    )
    assert settle.status_code == 201, settle.get_json()
    bills = settle.get_json()["data"].get("bills") or []
    assert bills, settle.get_json()
    bill = bills[0]
    assert bill.get("coupon_code") == "FLAT50"
    assert Decimal(str(bill.get("coupon_discount") or 0)) == Decimal("50.00")


def test_hotel_cannot_access_coupons(client):
    headers = login(client, "owner@hotela.com", "Owner@12345")
    res = client.get("/api/v1/coupons", headers=headers)
    assert res.status_code == 403, res.get_json()

    create = client.post(
        "/api/v1/coupons",
        headers=headers,
        json={
            "code": "HOTELX",
            "name": "Hotel blocked",
            "discount_type": "percent",
            "discount_value": 5,
        },
    )
    assert create.status_code == 403, create.get_json()


def test_biz17_cafe_coupon_isolation(client):
    """BIZ-17: coupons are cafe/addons_combos only — hotel blocked."""
    cafe_h = login(client, "owner@hotelb.com", "Owner@12345")
    hotel_h = login(client, "owner@hotela.com", "Owner@12345")

    ok = client.post(
        "/api/v1/coupons",
        headers=cafe_h,
        json={"code": "BIZ17C", "name": "Biz17", "discount_type": "amount", "discount_value": 10},
    )
    assert ok.status_code == 201, ok.get_json()

    blocked = client.get("/api/v1/coupons", headers=hotel_h)
    assert blocked.status_code == 403
