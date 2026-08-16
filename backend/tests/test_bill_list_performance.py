"""Performance-related regressions: bill list query shape."""

from sqlalchemy import event
from sqlalchemy.engine import Engine

from tests.conftest import login


def test_list_bills_does_not_n_plus_one_line_items(client, app):
    """List must not join every bill_item row (Bill.items is selectin + noload)."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Bill Perf Category"},
    ).get_json()["data"]["id"]

    item_ids = []
    for index in range(3):
        item = client.post(
            "/api/v1/items",
            headers=owner,
            json={
                "name": f"Bill Perf Item {index}",
                "category_id": category_id,
                "price": 20 + index,
                "gst_percentage": 5,
            },
        ).get_json()["data"]
        item_ids.append(item["id"])

    for bill_i in range(8):
        assert (
            client.post(
                "/api/v1/bills",
                headers=owner,
                json={
                    "payment_method": "cash",
                    "items": [
                        {"item_id": item_ids[0], "quantity": 1},
                        {"item_id": item_ids[1], "quantity": 2},
                        {"item_id": item_ids[2], "quantity": 1},
                    ],
                },
            ).status_code
            == 201
        ), bill_i

    statements = []

    def before_cursor(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(Engine, "before_cursor_execute", before_cursor)
    try:
        response = client.get(
            "/api/v1/bills",
            headers=owner,
            query_string={"per_page": 8},
        )
    finally:
        event.remove(Engine, "before_cursor_execute", before_cursor)

    assert response.status_code == 200
    assert len(response.get_json()["data"]) >= 8
    # Auth + count + bills(+creator) + one delivery-status batch —
    # must stay far below classic line-item N+1.
    assert len(statements) < 15, f"Too many SQL statements: {len(statements)}"
    joined_bill_items = [
        s for s in statements if "bill_items" in s.lower() and "join" in s.lower()
    ]
    assert not joined_bill_items, "bill list should not JOIN bill_items"
