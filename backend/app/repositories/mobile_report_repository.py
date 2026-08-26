"""Mobile / electronics sales dimensions (brand / model) and IMEI stock (BIZ-32)."""

from sqlalchemy import case, func, or_

from app.extensions import db
from app.models.bill import Bill, BillItem
from app.models.category import Category
from app.models.item import Item
from app.models.sales_return import KIND_EXCHANGE, KIND_RETURN, SalesReturn
from app.models.serial_unit import SerialUnit
from app.repositories.report_repository import ReportRepository


class MobileReportRepository:
    @staticmethod
    def _brand_label():
        return func.coalesce(func.nullif(func.trim(Item.brand), ""), "Unbranded")

    @staticmethod
    def _model_label():
        return func.coalesce(func.nullif(func.trim(Item.model_name), ""), "Unspecified model")

    @staticmethod
    def _sales_query(tenant_id, start, end, payment_method=None):
        query = (
            db.session.query(BillItem)
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
        return ReportRepository._payment_filter(query, payment_method)

    @staticmethod
    def _apply_filters(query, *, brand=None, model_name=None, category_id=None):
        if brand:
            token = brand.strip()
            if token.lower() == "unbranded":
                query = query.filter(
                    or_(
                        Item.id.is_(None),
                        Item.brand.is_(None),
                        func.trim(Item.brand) == "",
                    )
                )
            else:
                query = query.filter(func.lower(Item.brand) == token.lower())
        if model_name:
            token = model_name.strip()
            if token.lower() in {"unspecified model", "unspecified"}:
                query = query.filter(
                    or_(
                        Item.id.is_(None),
                        Item.model_name.is_(None),
                        func.trim(Item.model_name) == "",
                    )
                )
            else:
                query = query.filter(func.lower(Item.model_name) == token.lower())
        if category_id:
            query = query.filter(Item.category_id == category_id)
        return query

    @staticmethod
    def _grouped(tenant_id, start, end, label_expr, *, payment_method=None, **filters):
        query = MobileReportRepository._sales_query(
            tenant_id, start, end, payment_method=payment_method
        )
        query = MobileReportRepository._apply_filters(query, **filters)
        rows = (
            query.with_entities(
                label_expr,
                func.sum(BillItem.quantity),
                func.sum(BillItem.total),
                func.count(func.distinct(Bill.id)),
            )
            .group_by(label_expr)
            .order_by(func.sum(BillItem.total).desc())
            .all()
        )
        return [
            {
                "label": r[0],
                "quantity": float(r[1] or 0),
                "revenue": float(r[2] or 0),
                "bill_count": int(r[3] or 0),
            }
            for r in rows
        ]

    @staticmethod
    def by_brand(tenant_id, start, end, *, payment_method=None, **filters):
        rows = MobileReportRepository._grouped(
            tenant_id,
            start,
            end,
            MobileReportRepository._brand_label(),
            payment_method=payment_method,
            **filters,
        )
        return [{**row, "brand": row["label"]} for row in rows]

    @staticmethod
    def by_model(tenant_id, start, end, *, payment_method=None, **filters):
        rows = MobileReportRepository._grouped(
            tenant_id,
            start,
            end,
            MobileReportRepository._model_label(),
            payment_method=payment_method,
            **filters,
        )
        return [{**row, "model_name": row["label"]} for row in rows]

    @staticmethod
    def by_category(tenant_id, start, end, *, payment_method=None, **filters):
        label = func.coalesce(Category.name, "Uncategorized")
        rows = MobileReportRepository._grouped(
            tenant_id, start, end, label, payment_method=payment_method, **filters
        )
        return [{**row, "category_name": row["label"]} for row in rows]

    @staticmethod
    def serial_stock(tenant_id, *, brand=None, model_name=None, category_id=None, status=None):
        query = (
            db.session.query(
                SerialUnit.id,
                SerialUnit.serial,
                SerialUnit.status,
                Item.id,
                Item.name,
                Item.brand,
                Item.model_name,
            )
            .join(Item, Item.id == SerialUnit.item_id)
            .filter(SerialUnit.tenant_id == tenant_id, Item.tenant_id == tenant_id)
        )
        if brand:
            token = brand.strip()
            if token.lower() == "unbranded":
                query = query.filter(or_(Item.brand.is_(None), func.trim(Item.brand) == ""))
            else:
                query = query.filter(func.lower(Item.brand) == token.lower())
        if model_name:
            token = model_name.strip()
            if token.lower() in {"unspecified model", "unspecified"}:
                query = query.filter(
                    or_(Item.model_name.is_(None), func.trim(Item.model_name) == "")
                )
            else:
                query = query.filter(func.lower(Item.model_name) == token.lower())
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if status:
            query = query.filter(SerialUnit.status == status.strip().upper())
        rows = query.order_by(Item.name.asc(), SerialUnit.serial.asc()).limit(200).all()
        return [
            {
                "serial_unit_id": r[0],
                "serial": r[1],
                "status": r[2],
                "item_id": r[3],
                "item_name": r[4],
                "brand": r[5],
                "model_name": r[6],
            }
            for r in rows
        ]

    @staticmethod
    def serial_stock_summary(tenant_id):
        rows = (
            db.session.query(SerialUnit.status, func.count(SerialUnit.id))
            .filter(SerialUnit.tenant_id == tenant_id)
            .group_by(SerialUnit.status)
            .all()
        )
        summary = {"IN_STOCK": 0, "SOLD": 0, "QUARANTINE": 0}
        for status, count in rows:
            summary[status] = int(count or 0)
        return summary

    @staticmethod
    def returns_summary(tenant_id, start, end):
        row = (
            db.session.query(
                func.coalesce(
                    func.sum(case((SalesReturn.kind == KIND_RETURN, 1), else_=0)),
                    0,
                ),
                func.coalesce(
                    func.sum(case((SalesReturn.kind == KIND_EXCHANGE, 1), else_=0)),
                    0,
                ),
                func.coalesce(func.sum(SalesReturn.refund_amount), 0),
                func.coalesce(func.sum(SalesReturn.extra_payable), 0),
            )
            .filter(
                SalesReturn.tenant_id == tenant_id,
                SalesReturn.created_at >= start,
                SalesReturn.created_at < end,
            )
            .one()
        )
        return {
            "return_count": int(row[0] or 0),
            "exchange_count": int(row[1] or 0),
            "refund_amount": float(row[2] or 0),
            "extra_payable": float(row[3] or 0),
        }
