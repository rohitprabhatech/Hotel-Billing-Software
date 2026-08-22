"""Bill data access — tenant scoped."""

from datetime import datetime

from sqlalchemy import and_, case, func
from sqlalchemy.orm import joinedload, noload

from app.extensions import db
from app.models.bill import Bill, BillItem, BillNumberCounter
from app.models.bill_delivery import BillDelivery


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
        payment_method: str | None = None,
        whatsapp_status: str | None = None,
        email_status: str | None = None,
        customer_id: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Bill], int]:
        query = db.session.query(Bill).filter(Bill.tenant_id == tenant_id)
        if status:
            query = query.filter(Bill.status == status)
        if created_by:
            query = query.filter(Bill.created_by == created_by)
        if payment_method:
            query = query.filter(Bill.payment_method == payment_method)
        if customer_id:
            query = query.filter(Bill.customer_id == customer_id)
        if date_from:
            query = query.filter(Bill.created_at >= date_from)
        if date_to:
            query = query.filter(Bill.created_at <= date_to)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                (Bill.bill_number.ilike(like)) | (Bill.table_number.ilike(like))
            )
        if whatsapp_status:
            from sqlalchemy.orm import aliased

            WaDelivery = aliased(BillDelivery)
            wa_latest = (
                db.session.query(
                    BillDelivery.bill_id.label("bill_id"),
                    func.max(BillDelivery.created_at).label("max_created"),
                )
                .filter(
                    BillDelivery.tenant_id == tenant_id,
                    BillDelivery.delivery_method == "WHATSAPP",
                )
                .group_by(BillDelivery.bill_id)
                .subquery()
            )
            query = (
                query.join(wa_latest, Bill.id == wa_latest.c.bill_id)
                .join(
                    WaDelivery,
                    and_(
                        WaDelivery.bill_id == Bill.id,
                        WaDelivery.tenant_id == tenant_id,
                        WaDelivery.delivery_method == "WHATSAPP",
                        WaDelivery.created_at == wa_latest.c.max_created,
                    ),
                )
                .filter(WaDelivery.status == whatsapp_status)
            )
        if email_status:
            from sqlalchemy.orm import aliased

            EmailDelivery = aliased(BillDelivery)
            email_latest = (
                db.session.query(
                    BillDelivery.bill_id.label("bill_id"),
                    func.max(BillDelivery.created_at).label("max_created"),
                )
                .filter(
                    BillDelivery.tenant_id == tenant_id,
                    BillDelivery.delivery_method == "EMAIL",
                )
                .group_by(BillDelivery.bill_id)
                .subquery()
            )
            query = (
                query.join(email_latest, Bill.id == email_latest.c.bill_id)
                .join(
                    EmailDelivery,
                    and_(
                        EmailDelivery.bill_id == Bill.id,
                        EmailDelivery.tenant_id == tenant_id,
                        EmailDelivery.delivery_method == "EMAIL",
                        EmailDelivery.created_at == email_latest.c.max_created,
                    ),
                )
                .filter(EmailDelivery.status == email_status)
            )

        # Distinct count avoids inflated totals when delivery joins are present;
        # avoids wrapping a full ORM SELECT (with joined columns) in a subquery.
        total = (
            query.order_by(None)
            .with_entities(func.count(func.distinct(Bill.id)))
            .scalar()
            or 0
        )
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        bills = (
            query.options(noload(Bill.items), joinedload(Bill.creator))
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

    @staticmethod
    def today_sales_breakdown(tenant_id: str, day_start: datetime, day_end: datetime):
        row = (
            db.session.query(
                func.coalesce(func.sum(Bill.grand_total), 0),
                func.count(Bill.id),
                func.coalesce(
                    func.sum(
                        case((Bill.payment_method == "cash", Bill.grand_total), else_=0)
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        case((Bill.payment_method == "online", Bill.grand_total), else_=0)
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(case((Bill.payment_method == "cash", 1), else_=0)),
                    0,
                ),
                func.coalesce(
                    func.sum(case((Bill.payment_method == "online", 1), else_=0)),
                    0,
                ),
            )
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= day_start,
                Bill.created_at < day_end,
            )
            .one()
        )
        return {
            "total_sales": row[0],
            "bill_count": row[1],
            "cash_sales": row[2],
            "online_sales": row[3],
            "cash_bill_count": int(row[4] or 0),
            "online_bill_count": int(row[5] or 0),
        }
