"""Sales order persistence (BIZ-52)."""

from sqlalchemy import func

from app.extensions import db
from app.models.sales_order import SalesOrder, SalesOrderNumberCounter


class SalesOrderRepository:
    @staticmethod
    def get_by_id(tenant_id: str, order_id: str) -> SalesOrder | None:
        return SalesOrder.query.filter_by(tenant_id=tenant_id, id=order_id).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, status: str | None = None, page: int = 1, per_page: int = 100
    ) -> tuple[list[SalesOrder], int]:
        query = SalesOrder.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status.upper())
        total = query.with_entities(func.count(SalesOrder.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 100), 1), 200)
        rows = (
            query.order_by(SalesOrder.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(SalesOrderNumberCounter)
            .filter(SalesOrderNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = SalesOrderNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"SO-{sequence:05d}"

    @staticmethod
    def add(row: SalesOrder) -> SalesOrder:
        db.session.add(row)
        return row
