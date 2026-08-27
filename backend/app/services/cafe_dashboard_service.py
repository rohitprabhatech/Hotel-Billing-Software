"""Cafe owner dashboard aggregates (Sprint 4 — no schema changes)."""

from sqlalchemy import distinct, func

from app.constants.orders import ORDER_STATUS_BILLED
from app.constants.permissions import PERM_REPORTS
from app.extensions import db
from app.models.cafe_offer import Combo
from app.models.item import Item
from app.models.order import Order, OrderItem
from app.models.recipe import RecipeIngredient
from app.repositories.cafe_offer_repository import ComboRepository
from app.services.cafe_offer_service import ComboService
from app.services.report_service import ReportService
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

POPULAR_LIMIT = 8
LOW_INGREDIENT_LIMIT = 12


class CafeDashboardService:
    @staticmethod
    def dashboard(*, period: str = "last_7_days"):
        require_permission(PERM_REPORTS)
        ctx = require_request_context()
        summary = ReportService.summary(period=period or "last_7_days")
        start, end, *_ = ReportService._bounds(period or "last_7_days")

        return {
            "period": summary["period"],
            "label": summary["label"],
            "previous_label": summary.get("previous_label"),
            "current": summary["current"],
            "previous": summary["previous"],
            "day_wise": summary.get("day_wise") or [],
            "popular_items": summary.get("top_items") or [],
            "popular_combos": CafeDashboardService._combo_sales(ctx.tenant_id, start, end),
            "catalog_popular_combos": [
                ComboService.serialize(row)
                for row in ComboRepository.list_by_tenant(ctx.tenant_id)
                if row.is_popular and row.is_active
            ][:POPULAR_LIMIT],
            "low_ingredients": CafeDashboardService._low_ingredients(ctx.tenant_id),
            "inventory_health": summary.get("inventory_health") or {},
            "whatsapp_delivery": summary.get("whatsapp_delivery"),
            "email_delivery": summary.get("email_delivery"),
        }

    @staticmethod
    def _combo_sales(tenant_id: str, start, end) -> list[dict]:
        rows = (
            db.session.query(
                OrderItem.combo_id,
                Combo.name,
                func.count(distinct(OrderItem.order_id)),
                func.sum(OrderItem.line_total),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .outerjoin(Combo, Combo.id == OrderItem.combo_id)
            .filter(
                Order.tenant_id == tenant_id,
                OrderItem.tenant_id == tenant_id,
                Order.status == ORDER_STATUS_BILLED,
                Order.created_at >= start,
                Order.created_at < end,
                OrderItem.combo_id.isnot(None),
            )
            .group_by(OrderItem.combo_id, Combo.name)
            .order_by(func.sum(OrderItem.line_total).desc())
            .limit(POPULAR_LIMIT)
            .all()
        )
        return [
            {
                "combo_id": row[0],
                "name": row[1] or "Combo",
                "orders": int(row[2] or 0),
                "revenue": float(row[3] or 0),
            }
            for row in rows
        ]

    @staticmethod
    def _low_ingredients(tenant_id: str) -> list[dict]:
        rows = (
            db.session.query(Item)
            .join(RecipeIngredient, RecipeIngredient.ingredient_item_id == Item.id)
            .filter(
                Item.tenant_id == tenant_id,
                RecipeIngredient.tenant_id == tenant_id,
                Item.is_active.is_(True),
                Item.stock_quantity.isnot(None),
            )
            .distinct()
            .order_by(Item.name.asc())
            .all()
        )
        alerts = []
        for item in rows:
            stock = float(item.stock_quantity)
            minimum = (
                float(item.minimum_stock_level)
                if item.minimum_stock_level is not None
                else None
            )
            if stock <= 0:
                status = "out"
            elif minimum is not None and stock <= minimum:
                status = "low"
            else:
                continue
            alerts.append(
                {
                    "item_id": item.id,
                    "name": item.name,
                    "stock_quantity": stock,
                    "minimum_stock_level": minimum,
                    "uom": item.uom,
                    "status": status,
                }
            )
            if len(alerts) >= LOW_INGREDIENT_LIMIT:
                break
        alerts.sort(key=lambda row: (0 if row["status"] == "out" else 1, row["name"]))
        return alerts
