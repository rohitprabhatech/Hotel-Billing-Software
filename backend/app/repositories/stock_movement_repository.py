"""Stock movement data access — tenant scoped."""

from datetime import datetime

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.stock_movement import StockMovement


class StockMovementRepository:
    @staticmethod
    def add(row: StockMovement) -> StockMovement:
        db.session.add(row)
        return row

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        item_id: str | None = None,
        source: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[StockMovement], int]:
        query = db.session.query(StockMovement).filter(StockMovement.tenant_id == tenant_id)
        if item_id:
            query = query.filter(StockMovement.item_id == item_id)
        if source:
            query = query.filter(StockMovement.source == source)
        if date_from is not None:
            query = query.filter(StockMovement.created_at >= date_from)
        if date_to is not None:
            query = query.filter(StockMovement.created_at < date_to)
        total = query.count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        rows = (
            query.options(joinedload(StockMovement.item), joinedload(StockMovement.creator))
            .order_by(StockMovement.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total
