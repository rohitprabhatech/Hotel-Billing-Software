"""Sales return persistence (BIZ-27)."""

from sqlalchemy import func

from app.extensions import db
from app.models.sales_return import SalesReturn, SalesReturnCounter, SalesReturnItem


class SalesReturnRepository:
    @staticmethod
    def get_by_id(tenant_id: str, return_id: str) -> SalesReturn | None:
        return SalesReturn.query.filter_by(tenant_id=tenant_id, id=return_id).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, bill_id: str | None = None, page: int = 1, per_page: int = 50
    ) -> tuple[list[SalesReturn], int]:
        query = SalesReturn.query.filter_by(tenant_id=tenant_id)
        if bill_id:
            query = query.filter_by(bill_id=bill_id)
        total = query.with_entities(func.count(SalesReturn.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(SalesReturn.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def returned_qty_by_bill_item(tenant_id: str, bill_id: str) -> dict[str, float]:
        rows = (
            db.session.query(SalesReturnItem.bill_item_id, func.coalesce(func.sum(SalesReturnItem.quantity), 0))
            .join(SalesReturn, SalesReturn.id == SalesReturnItem.return_id)
            .filter(SalesReturn.tenant_id == tenant_id, SalesReturn.bill_id == bill_id)
            .group_by(SalesReturnItem.bill_item_id)
            .all()
        )
        return {bill_item_id: float(qty) for bill_item_id, qty in rows}

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(SalesReturnCounter)
            .filter(SalesReturnCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = SalesReturnCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"RET-{sequence:05d}"

    @staticmethod
    def add(row: SalesReturn) -> SalesReturn:
        db.session.add(row)
        return row

    @staticmethod
    def add_item(row: SalesReturnItem) -> SalesReturnItem:
        db.session.add(row)
        return row
