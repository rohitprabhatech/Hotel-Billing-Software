"""Clothing sales dimensions (brand / size / color / category) and returns."""

from sqlalchemy import case, func, or_

from app.extensions import db
from app.models.bill import Bill, BillItem
from app.models.category import Category
from app.models.item import Item
from app.models.item_variant import ItemVariant
from app.models.sales_return import KIND_EXCHANGE, KIND_RETURN, SalesReturn
from app.repositories.report_repository import ReportRepository


class ClothingReportRepository:
    @staticmethod
    def _brand_label():
        return func.coalesce(func.nullif(func.trim(ItemVariant.brand), ""), "Unbranded")

    @staticmethod
    def _size_label():
        return func.coalesce(func.nullif(func.trim(ItemVariant.size), ""), "Unsized")

    @staticmethod
    def _color_label():
        return func.coalesce(func.nullif(func.trim(ItemVariant.color), ""), "Uncolored")

    @staticmethod
    def _sales_query(tenant_id, start, end, payment_method=None):
        query = (
            db.session.query(BillItem)
            .join(Bill, Bill.id == BillItem.bill_id)
            .outerjoin(ItemVariant, ItemVariant.id == BillItem.variant_id)
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
    def _apply_filters(query, *, brand=None, size=None, color=None, category_id=None):
        if brand:
            token = brand.strip()
            if token.lower() == "unbranded":
                query = query.filter(
                    or_(
                        ItemVariant.id.is_(None),
                        ItemVariant.brand.is_(None),
                        func.trim(ItemVariant.brand) == "",
                    )
                )
            else:
                query = query.filter(func.lower(ItemVariant.brand) == token.lower())
        if size:
            query = query.filter(func.lower(ItemVariant.size) == size.strip().lower())
        if color:
            query = query.filter(func.lower(ItemVariant.color) == color.strip().lower())
        if category_id:
            query = query.filter(Item.category_id == category_id)
        return query

    @staticmethod
    def _grouped(tenant_id, start, end, label_expr, *, payment_method=None, **filters):
        query = ClothingReportRepository._sales_query(
            tenant_id, start, end, payment_method=payment_method
        )
        query = ClothingReportRepository._apply_filters(query, **filters)
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
        rows = ClothingReportRepository._grouped(
            tenant_id,
            start,
            end,
            ClothingReportRepository._brand_label(),
            payment_method=payment_method,
            **filters,
        )
        return [{**row, "brand": row["label"]} for row in rows]

    @staticmethod
    def by_size(tenant_id, start, end, *, payment_method=None, **filters):
        rows = ClothingReportRepository._grouped(
            tenant_id,
            start,
            end,
            ClothingReportRepository._size_label(),
            payment_method=payment_method,
            **filters,
        )
        return [{**row, "size": row["label"]} for row in rows]

    @staticmethod
    def by_color(tenant_id, start, end, *, payment_method=None, **filters):
        rows = ClothingReportRepository._grouped(
            tenant_id,
            start,
            end,
            ClothingReportRepository._color_label(),
            payment_method=payment_method,
            **filters,
        )
        return [{**row, "color": row["label"]} for row in rows]

    @staticmethod
    def by_category(tenant_id, start, end, *, payment_method=None, **filters):
        label = func.coalesce(Category.name, "Uncategorized")
        rows = ClothingReportRepository._grouped(
            tenant_id, start, end, label, payment_method=payment_method, **filters
        )
        return [{**row, "category_name": row["label"]} for row in rows]

    @staticmethod
    def variant_stock(tenant_id, *, brand=None, size=None, color=None, category_id=None):
        query = (
            db.session.query(
                ItemVariant.id,
                Item.id,
                Item.name,
                ItemVariant.size,
                ItemVariant.color,
                ItemVariant.brand,
                ItemVariant.stock_quantity,
                ItemVariant.is_active,
            )
            .join(Item, Item.id == ItemVariant.item_id)
            .filter(ItemVariant.tenant_id == tenant_id, Item.tenant_id == tenant_id)
        )
        if brand:
            token = brand.strip()
            if token.lower() == "unbranded":
                query = query.filter(
                    or_(ItemVariant.brand.is_(None), func.trim(ItemVariant.brand) == "")
                )
            else:
                query = query.filter(func.lower(ItemVariant.brand) == token.lower())
        if size:
            query = query.filter(func.lower(ItemVariant.size) == size.strip().lower())
        if color:
            query = query.filter(func.lower(ItemVariant.color) == color.strip().lower())
        if category_id:
            query = query.filter(Item.category_id == category_id)
        rows = (
            query.order_by(Item.name.asc(), ItemVariant.size.asc(), ItemVariant.color.asc())
            .limit(200)
            .all()
        )
        return [
            {
                "variant_id": r[0],
                "item_id": r[1],
                "item_name": r[2],
                "size": r[3],
                "color": r[4],
                "brand": r[5],
                "stock_quantity": float(r[6] or 0),
                "is_active": bool(r[7]),
            }
            for r in rows
        ]

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
