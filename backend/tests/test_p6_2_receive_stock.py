"""P6-2: receive stock + RECEIVE ledger + stock_status deep-link filters."""

import uuid

from tests.conftest import login
from tests.test_p3_1_stock_notifications import _category_and_item


def test_receive_stock_starts_tracking_and_adds(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    name = f"Recv {uuid.uuid4().hex[:8]}"
    item = _category_and_item(client, owner, name=name, stock=None)
    assert item["stock_quantity"] is None

    started = client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=owner,
        json={"quantity": 12, "reason": "Opening stock"},
    )
    assert started.status_code == 200, started.get_json()
    assert started.get_json()["data"]["stock_quantity"] == 12.0

    added = client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=owner,
        json={"quantity": 3, "reason": "Supplier"},
    )
    assert added.status_code == 200
    assert added.get_json()["data"]["stock_quantity"] == 15.0

    moves = client.get(
        "/api/v1/stock-movements",
        headers=owner,
        query_string={"item_id": item["id"], "source": "RECEIVE"},
    )
    assert moves.status_code == 200
    rows = moves.get_json()["data"]
    assert len(rows) >= 2
    assert all(r["source"] == "RECEIVE" for r in rows)
    assert rows[0]["delta"] == 3.0
    assert rows[0]["quantity_after"] == 15.0


def test_receive_stock_rejects_non_positive(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    item = _category_and_item(
        client, owner, name=f"BadRecv {uuid.uuid4().hex[:8]}", stock=5
    )
    zero = client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=owner,
        json={"quantity": 0},
    )
    assert zero.status_code == 400
    neg = client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=owner,
        json={"quantity": -2},
    )
    assert neg.status_code == 400


def test_billing_user_can_receive_stock(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    item = _category_and_item(
        client, owner, name=f"BillRecv {uuid.uuid4().hex[:8]}", stock=2, minimum=5
    )
    res = client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=billing,
        json={"quantity": 10, "reason": "Counter restock"},
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["stock_quantity"] == 12.0
