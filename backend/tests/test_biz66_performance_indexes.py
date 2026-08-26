"""Sprint BIZ-66 — performance indexes and POS catalog budgets."""

import time

from sqlalchemy import inspect

from app.constants.perf import (
    POS_CATALOG_MAX_LIMIT,
    POS_SEARCH_P95_MS,
    clamp_pos_catalog_limit,
)
from app.extensions import db
from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def test_pos_limit_clamp():
    assert clamp_pos_catalog_limit(None) == 50
    assert clamp_pos_catalog_limit(1) == 1
    assert clamp_pos_catalog_limit(999) == POS_CATALOG_MAX_LIMIT
    assert POS_SEARCH_P95_MS == 200


def test_perf_indexes_present_on_models(app):
    with app.app_context():
        insp = inspect(db.engine)
        expected = {
            "items": "ix_items_tenant_active_name",
            "warehouse_stocks": "ix_warehouse_stocks_tenant_item",
            "stock_movements": "ix_stock_movements_tenant_item_created",
            "bills": "ix_bills_tenant_created_at",
            "serial_units": "ix_serial_units_tenant_status_received",
        }
        for table, name in expected.items():
            names = {idx["name"] for idx in insp.get_indexes(table)}
            assert name in names, (table, name, names)


def test_pos_catalog_enforces_max_limit(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "grocery_kirana")
    cat = client.post(
        "/api/v1/categories", headers=owner, json={"name": "Perf Cat"}
    ).get_json()["data"]["id"]
    for i in range(12):
        assert (
            client.post(
                "/api/v1/items",
                headers=owner,
                json={
                    "name": f"Perf Oil {i}",
                    "category_id": cat,
                    "price": "10",
                    "gst_percentage": "0",
                    "stock_quantity": "5",
                    "barcode": f"8909000066{i:02d}",
                },
            ).status_code
            == 201
        )

    started = time.perf_counter()
    response = client.get(
        "/api/v1/grocery/pos-catalog",
        headers=owner,
        query_string={"q": "Oil", "limit": 500},
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    assert response.status_code == 200, response.get_json()
    items = response.get_json()["data"]["items"]
    assert len(items) <= POS_CATALOG_MAX_LIMIT
    # CI budget (loose); staging p95 is POS_SEARCH_P95_MS.
    assert elapsed_ms < 2000, elapsed_ms

    barcode = client.get(
        "/api/v1/items/by-barcode/890900006601",
        headers=owner,
    )
    assert barcode.status_code == 200, barcode.get_json()
