"""Tenant-scoped sales report queries."""

from datetime import datetime, timedelta

from sqlalchemy import and_, case, func

from app.extensions import db
from app.models.bill import Bill, BillItem
from app.models.category import Category
from app.models.item import Item
from app.utils.periods import get_tz, report_timezone_name


def _mysql_tz_offset(tz_name: str) -> str:
    tz = get_tz(tz_name)
    offset = datetime.now(tz).utcoffset()
    if offset is None:
        return "+00:00"
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours, rem = divmod(total_seconds, 3600)
    minutes = rem // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


class ReportRepository:
    @staticmethod
    def _payment_filter(query, payment_method: str | None):
        if payment_method:
            return query.filter(Bill.payment_method == payment_method)
        return query

    @staticmethod
    def period_metrics(tenant_id: str, start, end, payment_method: str | None = None) -> dict:
        query = db.session.query(
            func.coalesce(
                func.sum(
                    case((Bill.status == "FINALIZED", Bill.grand_total), else_=0)
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case((Bill.status == "FINALIZED", 1), else_=0)
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case((Bill.status == "FINALIZED", Bill.discount), else_=0)
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case((Bill.status == "FINALIZED", Bill.gst_amount), else_=0)
                ),
                0,
            ),
            func.coalesce(
                func.sum(case((Bill.status == "CANCELLED", 1), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Bill.status == "FINALIZED",
                                Bill.payment_method == "cash",
                            ),
                            Bill.grand_total,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Bill.status == "FINALIZED",
                                Bill.payment_method == "online",
                            ),
                            Bill.grand_total,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Bill.status == "FINALIZED",
                                Bill.payment_method == "cash",
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Bill.status == "FINALIZED",
                                Bill.payment_method == "online",
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Bill.status == "FINALIZED",
                                Bill.payment_method == "credit",
                            ),
                            Bill.grand_total,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                Bill.status == "FINALIZED",
                                Bill.payment_method == "credit",
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
        ).filter(
            Bill.tenant_id == tenant_id,
            Bill.created_at >= start,
            Bill.created_at < end,
        )
        query = ReportRepository._payment_filter(query, payment_method)
        row = query.one()

        sales = row[0] or 0
        bill_count = int(row[1] or 0)
        discount = row[2] or 0
        gst = row[3] or 0
        cancelled = int(row[4] or 0)
        cash_sales = row[5] or 0
        online_sales = row[6] or 0
        cash_bill_count = int(row[7] or 0)
        online_bill_count = int(row[8] or 0)
        credit_sales = row[9] or 0
        credit_bill_count = int(row[10] or 0)
        average = float(sales) / bill_count if bill_count else 0.0

        items_query = (
            db.session.query(func.coalesce(func.sum(BillItem.quantity), 0))
            .join(Bill, Bill.id == BillItem.bill_id)
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= start,
                Bill.created_at < end,
            )
        )
        items_query = ReportRepository._payment_filter(items_query, payment_method)
        items_sold = items_query.scalar()

        return {
            "total_sales": float(sales),
            "bill_count": bill_count,
            "total_discount": float(discount),
            "total_gst": float(gst),
            "average_bill": round(average, 2),
            "items_sold": float(items_sold or 0),
            "cancelled_bills": cancelled,
            "cash_sales": float(cash_sales),
            "online_sales": float(online_sales),
            "cash_bill_count": cash_bill_count,
            "online_bill_count": online_bill_count,
            "credit_sales": float(credit_sales),
            "credit_bill_count": credit_bill_count,
        }

    @staticmethod
    def item_wise(tenant_id: str, start, end, payment_method: str | None = None) -> list[dict]:
        query = (
            db.session.query(
                BillItem.item_name,
                func.sum(BillItem.quantity),
                func.sum(BillItem.total),
            )
            .join(Bill, Bill.id == BillItem.bill_id)
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= start,
                Bill.created_at < end,
            )
        )
        query = ReportRepository._payment_filter(query, payment_method)
        rows = (
            query.group_by(BillItem.item_name)
            .order_by(func.sum(BillItem.total).desc())
            .all()
        )
        return [
            {
                "item_name": r[0],
                "quantity": float(r[1] or 0),
                "revenue": float(r[2] or 0),
            }
            for r in rows
        ]

    @staticmethod
    def category_wise(
        tenant_id: str, start, end, payment_method: str | None = None
    ) -> list[dict]:
        category_name = func.coalesce(Category.name, "Uncategorized")
        query = (
            db.session.query(
                category_name,
                func.sum(BillItem.quantity),
                func.sum(BillItem.total),
            )
            .join(Bill, Bill.id == BillItem.bill_id)
            .outerjoin(Item, Item.id == BillItem.item_id)
            .outerjoin(Category, Category.id == Item.category_id)
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= start,
                Bill.created_at < end,
            )
        )
        query = ReportRepository._payment_filter(query, payment_method)
        rows = (
            query.group_by(category_name)
            .order_by(func.sum(BillItem.total).desc())
            .all()
        )
        return [
            {
                "category_name": r[0],
                "quantity": float(r[1] or 0),
                "revenue": float(r[2] or 0),
            }
            for r in rows
        ]

    @staticmethod
    def day_wise(
        tenant_id: str,
        start,
        end,
        payment_method: str | None = None,
        *,
        tz_name: str = "Asia/Kolkata",
    ) -> list[dict]:
        """Aggregate finalized sales by local calendar day (tenant timezone)."""
        bind = db.session.get_bind()
        dialect = bind.dialect.name if bind is not None else "sqlite"
        resolved_tz = report_timezone_name(tz_name)
        # Bills store UTC-naive timestamps; bucket by tenant local calendar day.
        if dialect == "mysql":
            offset = _mysql_tz_offset(resolved_tz)
            day_expr = func.date(func.convert_tz(Bill.created_at, "+00:00", offset))
        else:
            tz = get_tz(resolved_tz)
            offset_minutes = int((datetime.now(tz).utcoffset() or timedelta()).total_seconds() // 60)
            day_expr = func.date(Bill.created_at, f"+{offset_minutes} minutes")

        query = (
            db.session.query(
                day_expr,
                func.coalesce(func.sum(Bill.grand_total), 0),
                func.count(Bill.id),
            )
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= start,
                Bill.created_at < end,
            )
        )
        query = ReportRepository._payment_filter(query, payment_method)
        rows = query.group_by(day_expr).order_by(day_expr.asc()).all()
        return [
            {
                "date": str(r[0]),
                "total_sales": float(r[1] or 0),
                "bill_count": int(r[2] or 0),
            }
            for r in rows
        ]

    @staticmethod
    def bill_rows(
        tenant_id: str,
        start,
        end,
        payment_method: str | None = None,
        *,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Bill], int]:
        query = db.session.query(Bill).filter(
            Bill.tenant_id == tenant_id,
            Bill.created_at >= start,
            Bill.created_at < end,
        )
        query = ReportRepository._payment_filter(query, payment_method)
        total = query.count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 200)
        rows = (
            query.order_by(Bill.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total
