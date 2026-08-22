"""Wastage entry data access (BIZ-18)."""

from datetime import date

from sqlalchemy import func

from app.extensions import db
from app.models.wastage import WastageEntry


class WastageRepository:
    @staticmethod
    def get_by_id_and_tenant(wastage_id: str, tenant_id: str) -> WastageEntry | None:
        return (
            db.session.query(WastageEntry)
            .filter(WastageEntry.id == wastage_id, WastageEntry.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        item_id: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[WastageEntry], int]:
        query = db.session.query(WastageEntry).filter(WastageEntry.tenant_id == tenant_id)
        if item_id:
            query = query.filter(WastageEntry.item_id == item_id)
        if from_date:
            query = query.filter(WastageEntry.wastage_date >= from_date)
        if to_date:
            query = query.filter(WastageEntry.wastage_date <= to_date)
        total = query.with_entities(func.count(WastageEntry.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(WastageEntry.wastage_date.desc(), WastageEntry.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def summary_by_tenant(
        tenant_id: str,
        *,
        from_date: date | None = None,
        to_date: date | None = None,
        created_from=None,
        created_to=None,
    ) -> dict:
        query = db.session.query(WastageEntry).filter(WastageEntry.tenant_id == tenant_id)
        if from_date:
            query = query.filter(WastageEntry.wastage_date >= from_date)
        if to_date:
            query = query.filter(WastageEntry.wastage_date <= to_date)
        if created_from is not None:
            query = query.filter(WastageEntry.created_at >= created_from)
        if created_to is not None:
            query = query.filter(WastageEntry.created_at < created_to)

        totals = query.with_entities(
            func.count(WastageEntry.id),
            func.coalesce(func.sum(WastageEntry.quantity), 0),
        ).one()
        entry_count = int(totals[0] or 0)
        total_quantity = float(totals[1] or 0)

        by_item = (
            query.with_entities(
                WastageEntry.item_id,
                WastageEntry.item_name,
                func.sum(WastageEntry.quantity).label("quantity"),
                func.count(WastageEntry.id).label("entry_count"),
            )
            .group_by(WastageEntry.item_id, WastageEntry.item_name)
            .order_by(func.sum(WastageEntry.quantity).desc())
            .limit(10)
            .all()
        )
        top_items = [
            {
                "item_id": row.item_id,
                "item_name": row.item_name,
                "quantity": float(row.quantity or 0),
                "entry_count": int(row.entry_count or 0),
            }
            for row in by_item
        ]
        return {
            "entry_count": entry_count,
            "total_quantity": total_quantity,
            "top_items": top_items,
        }

    @staticmethod
    def add(entry: WastageEntry) -> WastageEntry:
        db.session.add(entry)
        return entry
