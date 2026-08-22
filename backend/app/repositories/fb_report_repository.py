"""F&B report queries (BIZ-18)."""

from sqlalchemy import func

from app.constants.orders import ORDER_CHANNEL_LABELS
from app.extensions import db
from app.models.bill import Bill
from app.models.dining_table import DiningTable
from app.models.order import Order
from app.repositories.wastage_repository import WastageRepository


class FbReportRepository:
    @staticmethod
    def channel_wise(tenant_id: str, start, end) -> list[dict]:
        channel_expr = func.coalesce(Order.channel, "direct")
        rows = (
            db.session.query(
                channel_expr,
                func.coalesce(func.sum(Bill.grand_total), 0),
                func.count(Bill.id),
            )
            .outerjoin(Order, Order.id == Bill.order_id)
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= start,
                Bill.created_at < end,
            )
            .group_by(channel_expr)
            .order_by(func.sum(Bill.grand_total).desc())
            .all()
        )
        return [
            {
                "channel": row[0],
                "channel_label": ORDER_CHANNEL_LABELS.get(row[0], "Direct / Counter"),
                "total_sales": float(row[1] or 0),
                "bill_count": int(row[2] or 0),
            }
            for row in rows
        ]

    @staticmethod
    def table_wise(tenant_id: str, start, end) -> list[dict]:
        table_expr = func.coalesce(DiningTable.code, Bill.table_number, "Walk-in")
        rows = (
            db.session.query(
                table_expr,
                func.coalesce(func.sum(Bill.grand_total), 0),
                func.count(Bill.id),
            )
            .outerjoin(Order, Order.id == Bill.order_id)
            .outerjoin(DiningTable, DiningTable.id == Order.dining_table_id)
            .filter(
                Bill.tenant_id == tenant_id,
                Bill.status == "FINALIZED",
                Bill.created_at >= start,
                Bill.created_at < end,
            )
            .group_by(table_expr)
            .order_by(func.sum(Bill.grand_total).desc())
            .limit(50)
            .all()
        )
        return [
            {
                "table_code": row[0],
                "total_sales": float(row[1] or 0),
                "bill_count": int(row[2] or 0),
            }
            for row in rows
        ]

    @staticmethod
    def wastage_summary(tenant_id: str, start, end) -> dict:
        return WastageRepository.summary_by_tenant(
            tenant_id,
            created_from=start,
            created_to=end,
        )
