"""Purchase order persistence (BIZ-52)."""

from sqlalchemy import func

from app.extensions import db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderNumberCounter


class PurchaseOrderRepository:
    @staticmethod
    def get_by_id(tenant_id: str, order_id: str) -> PurchaseOrder | None:
        return PurchaseOrder.query.filter_by(tenant_id=tenant_id, id=order_id).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, status: str | None = None, page: int = 1, per_page: int = 100
    ) -> tuple[list[PurchaseOrder], int]:
        query = PurchaseOrder.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status.upper())
        total = query.with_entities(func.count(PurchaseOrder.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 100), 1), 200)
        rows = (
            query.order_by(PurchaseOrder.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(PurchaseOrderNumberCounter)
            .filter(PurchaseOrderNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = PurchaseOrderNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"PO-{sequence:05d}"

    @staticmethod
    def add(row: PurchaseOrder) -> PurchaseOrder:
        db.session.add(row)
        return row
