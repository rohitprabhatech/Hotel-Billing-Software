"""Performance-related regressions: item list query shape."""

from sqlalchemy import event
from sqlalchemy.engine import Engine

from tests.conftest import login


def test_list_items_query_count_stays_bounded(client, app):
    """Eager category/creator + category map should avoid per-row N+1."""
    owner = login(client, "owner@hotela.com", "Owner@12345")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Perf Category"},
    ).get_json()["data"]["id"]

    for index in range(12):
        assert (
            client.post(
                "/api/v1/items",
                headers=owner,
                json={
                    "name": f"Perf Item {index}",
                    "category_id": category_id,
                    "price": 10 + index,
                    "gst_percentage": 5,
                },
            ).status_code
            == 201
        )

    statements = []

    def before_cursor(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(Engine, "before_cursor_execute", before_cursor)
    try:
        response = client.get(
            "/api/v1/items",
            headers=owner,
            query_string={"per_page": 12},
        )
    finally:
        event.remove(Engine, "before_cursor_execute", before_cursor)

    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 12
    # Auth + count + items join + categories map (+ optional role lookups) —
    # must stay well below classic N+1 (~1 + 12*2).
    assert len(statements) < 20, f"Too many SQL statements: {len(statements)}"
