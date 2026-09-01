"""Sprint BIZ-61 — cross-business report registry and perf guards."""

import time
from datetime import date, timedelta

from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def test_available_reports_module_aware(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")

    _switch(client, owner, "hotel_restaurant")
    restaurant = client.get("/api/v1/reports/available", headers=owner)
    assert restaurant.status_code == 200, restaurant.get_json()
    body = restaurant.get_json()["data"]
    ids = {row["id"] for row in body["reports"]}
    assert "sales" in ids
    assert "fb" in ids
    assert "apparel" not in ids
    assert "travel_commission" not in ids
    assert body["limits"]["max_custom_range_days"] == 366
    assert any("ix_bills_tenant_status_created_at" in note for note in body["index_notes"])

    _switch(client, owner, "clothing")
    clothing = client.get("/api/v1/reports/available", headers=owner).get_json()["data"]
    clothing_ids = {row["id"] for row in clothing["reports"]}
    assert "sales" in clothing_ids
    assert "apparel" in clothing_ids
    assert "fb" not in clothing_ids
    assert "mobile" not in clothing_ids

    _switch(client, owner, "travel_agency")
    travel = client.get("/api/v1/reports/available", headers=owner).get_json()["data"]
    travel_ids = {row["id"] for row in travel["reports"]}
    assert "sales" in travel_ids
    assert "travel_commission" in travel_ids
    assert "travel_bookings" in travel_ids
    assert "tour_packages" in travel_ids
    assert "fb" not in travel_ids
    assert all(row["kind"] == "link" for row in travel["link_reports"])

    _switch(client, owner, "stationery")
    stationery = client.get("/api/v1/reports/available", headers=owner).get_json()["data"]
    stationery_ids = {row["id"] for row in stationery["reports"]}
    assert "sales" in stationery_ids
    assert "kirana" not in stationery_ids
    assert "outstanding" in stationery_ids
    hub_views = {row["view"] for row in stationery["hub_reports"]}
    assert hub_views == {"sales"}


def test_custom_range_perf_budget_rejected(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    start = date(2020, 1, 1)
    end = start + timedelta(days=400)
    response = client.get(
        "/api/v1/reports/custom-sales",
        headers=owner,
        query_string={"from": start.isoformat(), "to": end.isoformat()},
    )
    assert response.status_code == 400, response.get_json()
    assert "366" in response.get_json()["error"]["message"]


def test_custom_range_within_budget_and_bills_pagination(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    cat = client.post(
        "/api/v1/categories", headers=owner, json={"name": "BIZ61 Cat"}
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "BIZ61 Item",
            "category_id": cat,
            "price": 100,
            "gst_percentage": 0,
        },
    ).get_json()["data"]["id"]
    for _ in range(3):
        assert (
            client.post(
                "/api/v1/bills",
                headers=billing,
                json={"items": [{"item_id": item, "quantity": 1}], "discount": 0},
            ).status_code
            == 201
        )

    today = date.today()
    start = today - timedelta(days=30)
    began = time.perf_counter()
    response = client.get(
        "/api/v1/reports/custom-sales",
        headers=owner,
        query_string={
            "from": start.isoformat(),
            "to": today.isoformat(),
            "page": 1,
            "per_page": 2,
        },
    )
    elapsed = time.perf_counter() - began
    assert response.status_code == 200, response.get_json()
    assert elapsed < 5.0, f"report too slow: {elapsed:.2f}s"
    data = response.get_json()["data"]
    meta = data["bills_meta"]
    assert meta["page"] == 1
    assert meta["per_page"] == 2
    assert meta["total"] >= 3
    assert len(data["bills"]) == 2
    assert response.get_json()["meta"]["total"] >= 3

    page2 = client.get(
        "/api/v1/reports/custom-sales",
        headers=owner,
        query_string={
            "from": start.isoformat(),
            "to": today.isoformat(),
            "page": 2,
            "per_page": 2,
        },
    )
    assert page2.status_code == 200
    assert page2.get_json()["data"]["bills_meta"]["page"] == 2
    assert len(page2.get_json()["data"]["bills"]) >= 1


def test_billing_cannot_list_available_reports(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "grocery_kirana")
    assert client.get("/api/v1/reports/available", headers=billing).status_code == 403
