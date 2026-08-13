"""Bill data access — tenant scoped."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.bill import Bill, BillItem, BillNumberCounter


class BillRepository:
    @staticmethod
    def get_by_id_and_tenant(bill_id: str, tenant_id: str) -> Bill | None:
        return (
            db.session.query(Bill)
            .options(joinedload(Bill.items), joinedload(Bill.creator))
            .filter(Bill.id == bill_id, Bill.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        status: str | None = None,
        created_by: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Bill], int]:
        query = db.session.query(Bill).filter(Bill.tenant_id == tenant_id)
        if status:
            query = query.filter(Bill.status == status)
        if created_by:
            query = query.filter(Bill.created_by == created_by)
        if date_from:
            query = query.filter(Bill.created_at >= date_from)
        if date_to:
            query = query.filter(Bill.created_at <= date_to)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                (Bill.bill_number.ilike(like)) | (Bill.table_number.ilike(like))
            )

        total = query.count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        bills = (
            query.options(joinedload(Bill.creator))
            .order_by(Bill.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return bills, total

    @staticmethod
    def allocate_bill_number(tenant_id: str, prefix: str | None) -> tuple[int, str]:
        counter = (
            db.session.query(BillNumberCounter)
            .filter(BillNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = BillNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()

        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()

        prefix = prefix or ""
        bill_number = f"{prefix}{sequence}" if prefix else str(sequence)
        return sequence, bill_number

    @staticmethod
    def add_bill(bill: Bill) -> Bill:
        db.session.add(bill)
        return bill

    @staticmethod
    def add_item(item: BillItem) -> BillItem:
        db.session.add(item)
        return item

    @staticmethod
    def today_sales_total(tenant_id: str, day_start: datetime, day_end: datetime):
        row = (
            db.session.query(
                func.coalesce(func.sum(Bill.grand_total), 0),
                func.count(Bill.id),
            )
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= day_start,
                Bill.created_at < day_end,
            )
            .one()
        )
        return row[0], row[1]
