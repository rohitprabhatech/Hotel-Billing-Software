"""P6-1: stock movement ledger + stock_status filters."""

import uuid

from tests.conftest import login
from tests.test_p3_1_stock_notifications import _category_and_item


def test_adjust_and_bill_create_stock_movements(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    name = f"Move {uuid.uuid4().hex[:8]}"
    item = _category_and_item(client, owner, name=name, stock=20, minimum=5)

    adj = client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": 5, "reason": "Received shipment"},
    )
    assert adj.status_code == 200, adj.get_json()
    assert adj.get_json()["data"]["stock_quantity"] == 25.0

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": 3}],
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_id = bill.get_json()["data"]["id"]

    cancelled = client.post(
        f"/api/v1/bills/{bill_id}/cancel",
        headers=owner,
        json={"reason": "Customer left"},
    )
    assert cancelled.status_code == 200, cancelled.get_json()

    moves = client.get(
        "/api/v1/stock-movements",
        headers=owner,
        query_string={"item_id": item["id"], "per_page": 50},
    )
    assert moves.status_code == 200, moves.get_json()
    rows = moves.get_json()["data"]
    sources = [r["source"] for r in rows]
    assert "ADJUST" in sources
    assert "BILL" in sources
    assert "CANCEL" in sources

    adjust_row = next(r for r in rows if r["source"] == "ADJUST")
    assert adjust_row["delta"] == 5.0
    assert adjust_row["quantity_after"] == 25.0
    assert "shipment" in (adjust_row["reason"] or "").lower()

    bill_row = next(r for r in rows if r["source"] == "BILL")
    assert bill_row["delta"] == -3.0
    assert bill_row["reference_type"] == "BILL"
    assert bill_row["reference_id"] == bill_id

    cancel_row = next(r for r in rows if r["source"] == "CANCEL")
    assert cancel_row["delta"] == 3.0


def test_stock_movements_owner_only(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(
        client, owner, name=f"Own {uuid.uuid4().hex[:8]}", stock=8
    )
    client.post(
        f"/api/v1/items/{item['id']}/adjust-stock",
        headers=owner,
        json={"delta": 1},
    )
    forbidden = client.get("/api/v1/stock-movements", headers=billing)
    assert forbidden.status_code == 403


def test_items_stock_status_filter(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    suffix = uuid.uuid4().hex[:6]
    low = _category_and_item(
        client, owner, name=f"Low-{suffix}", stock=3, minimum=5
    )
    out = _category_and_item(
        client, owner, name=f"Out-{suffix}", stock=0, minimum=2
    )
    tracked = _category_and_item(
        client, owner, name=f"Ok-{suffix}", stock=20, minimum=5
    )
    _category_and_item(client, owner, name=f"None-{suffix}", stock=None)

    low_list = client.get(
        "/api/v1/items",
        headers=owner,
        query_string={"stock_status": "low", "q": suffix},
    ).get_json()["data"]
    assert {i["id"] for i in low_list} == {low["id"]}

    out_list = client.get(
        "/api/v1/items",
        headers=owner,
        query_string={"stock_status": "out", "q": suffix},
    ).get_json()["data"]
    assert {i["id"] for i in out_list} == {out["id"]}

    tracked_list = client.get(
        "/api/v1/items",
        headers=owner,
        query_string={"stock_status": "tracked", "q": suffix},
    ).get_json()["data"]
    ids = {i["id"] for i in tracked_list}
    assert low["id"] in ids and out["id"] in ids and tracked["id"] in ids
    assert len(ids) == 3
