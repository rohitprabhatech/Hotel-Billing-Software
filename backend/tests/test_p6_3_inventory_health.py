"""P6-3: inventory health KPIs + stock movement date filters."""

import uuid
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.stock_movement import StockMovement
from tests.conftest import login
from tests.test_p3_1_stock_notifications import _category_and_item


def test_report_summary_includes_inventory_health(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    suffix = uuid.uuid4().hex[:6]
    _category_and_item(client, owner, name=f"Low-{suffix}", stock=2, minimum=5)
    _category_and_item(client, owner, name=f"Out-{suffix}", stock=0, minimum=1)
    _category_and_item(client, owner, name=f"Ok-{suffix}", stock=20, minimum=5)
    _category_and_item(client, owner, name=f"None-{suffix}", stock=None)

    summary = client.get(
        "/api/v1/reports/summary",
        headers=owner,
        query_string={"period": "today"},
    )
    assert summary.status_code == 200, summary.get_json()
    health = summary.get_json()["data"]["inventory_health"]
    assert health["tracked"] >= 3
    assert health["untracked"] >= 1
    assert health["low"] >= 1
    assert health["out"] >= 1
    assert health["total_items"] == health["tracked"] + health["untracked"]


def test_stock_movements_date_filter(client, app):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    item = _category_and_item(
        client, owner, name=f"DateMov {uuid.uuid4().hex[:8]}", stock=10
    )
    client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=owner,
        json={"quantity": 4, "reason": "today receive"},
    )

    with app.app_context():
        old = (
            db.session.query(StockMovement)
            .filter(StockMovement.item_id == item["id"])
            .order_by(StockMovement.created_at.desc())
            .first()
        )
        assert old is not None
        old.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=10)
        db.session.commit()

    client.post(
        f"/api/v1/items/{item['id']}/receive-stock",
        headers=owner,
        json={"quantity": 1, "reason": "fresh receive"},
    )

    today = datetime.now().strftime("%Y-%m-%d")
    filtered = client.get(
        "/api/v1/stock-movements",
        headers=owner,
        query_string={"item_id": item["id"], "from": today, "to": today},
    )
    assert filtered.status_code == 200
    rows = filtered.get_json()["data"]
    assert len(rows) == 1
    assert rows[0]["delta"] == 1.0
    assert "fresh" in (rows[0]["reason"] or "")
