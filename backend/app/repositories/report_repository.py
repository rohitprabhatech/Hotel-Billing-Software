"""Tenant-scoped sales report queries."""

from sqlalchemy import and_, case, func

from app.extensions import db
from app.models.bill import Bill, BillItem


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
    def day_wise(tenant_id: str, start, end, payment_method: str | None = None) -> list[dict]:
        day_expr = func.date(Bill.created_at)
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
    def bill_rows(tenant_id: str, start, end, payment_method: str | None = None) -> list[Bill]:
        query = (
            db.session.query(Bill)
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.created_at >= start,
                Bill.created_at < end,
            )
        )
        query = ReportRepository._payment_filter(query, payment_method)
        return query.order_by(Bill.created_at.desc()).limit(200).all()
