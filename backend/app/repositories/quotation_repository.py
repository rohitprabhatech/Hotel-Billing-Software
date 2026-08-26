"""Quotation persistence (BIZ-36)."""

from sqlalchemy import func

from app.extensions import db
from app.models.quotation import Quotation, QuotationNumberCounter


class QuotationRepository:
    @staticmethod
    def get_by_id(tenant_id: str, quotation_id: str) -> Quotation | None:
        return Quotation.query.filter_by(tenant_id=tenant_id, id=quotation_id).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, status: str | None = None, page: int = 1, per_page: int = 100
    ) -> tuple[list[Quotation], int]:
        query = Quotation.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status.upper())
        total = query.with_entities(func.count(Quotation.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 100), 1), 200)
        rows = (
            query.order_by(Quotation.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(QuotationNumberCounter)
            .filter(QuotationNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = QuotationNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"QT-{sequence:05d}"

    @staticmethod
    def add(row: Quotation) -> Quotation:
        db.session.add(row)
        return row
