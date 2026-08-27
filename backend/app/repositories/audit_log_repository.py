"""Tenant-scoped audit log queries."""

from datetime import datetime

from sqlalchemy import String, cast, func, or_

from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.bill import Bill


# Frontend activity-type filter → entity types / actions
ACTIVITY_CATEGORY_FILTERS: dict[str, dict] = {
    "customer": {"entity_types": ["CUSTOMER"]},
    "item": {"entity_types": ["ITEM"]},
    "category": {"entity_types": ["CATEGORY"]},
    "billing": {"entity_types": ["BILL"]},
    "payment": {
        "actions": [
            "COLLECT_CREDIT_PAYMENT",
            "CREDIT_SALE",
            "CREDIT_PURCHASE",
            "PAY_SUPPLIER_CREDIT",
            "CREDIT_BILL_CANCEL",
            "CREDIT_PURCHASE_CANCEL",
            "TRAVEL_BOOKING_PAYMENT",
        ]
    },
    "expense": {"entity_types": ["EXPENSE"]},
    "recipe": {"entity_types": ["RECIPE"]},
    "wastage": {"entity_types": ["WASTAGE"]},
    "table": {"entity_types": ["DINING_TABLE", "ORDER", "KOT"]},
    "user": {"entity_types": ["USER"]},
    "inventory": {"entity_types": ["STOCK_MOVEMENT"]},
}


class AuditLogRepository:
    @staticmethod
    def get_by_id_and_tenant(log_id: str, tenant_id: str) -> AuditLog | None:
        return (
            db.session.query(AuditLog)
            .filter(
                AuditLog.id == log_id,
                AuditLog.tenant_id == tenant_id,
                AuditLog.is_deleted.is_(False),
            )
            .first()
        )

    @staticmethod
    def soft_delete(log_id: str, tenant_id: str) -> bool:
        row = (
            db.session.query(AuditLog)
            .filter(
                AuditLog.id == log_id,
                AuditLog.tenant_id == tenant_id,
                AuditLog.is_deleted.is_(False),
            )
            .first()
        )
        if row is None:
            return False
        row.is_deleted = True
        return True

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        user_id: str | None = None,
        action: str | None = None,
        actions: list[str] | None = None,
        entity_type: str | None = None,
        entity_types: list[str] | None = None,
        entity_id: str | None = None,
        bill_number: str | None = None,
        q: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[AuditLog], int]:
        query = db.session.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.is_deleted.is_(False),
        )

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if actions:
            query = query.filter(AuditLog.action.in_(actions))
        elif action:
            query = query.filter(AuditLog.action == action)
        if entity_types:
            query = query.filter(AuditLog.entity_type.in_(entity_types))
        elif entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if date_from:
            query = query.filter(AuditLog.created_at >= date_from)
        if date_to:
            query = query.filter(AuditLog.created_at < date_to)

        if bill_number:
            like = f"%{bill_number.strip()}%"
            bill_ids = [
                row[0]
                for row in db.session.query(Bill.id)
                .filter(Bill.tenant_id == tenant_id, Bill.bill_number.ilike(like))
                .all()
            ]
            if not bill_ids:
                return [], 0
            query = query.filter(
                AuditLog.entity_type == "BILL",
                AuditLog.entity_id.in_(bill_ids),
            )

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    AuditLog.action.ilike(like),
                    AuditLog.user_name.ilike(like),
                    AuditLog.entity_type.ilike(like),
                    cast(AuditLog.new_data, String).ilike(like),
                    cast(AuditLog.old_data, String).ilike(like),
                )
            )

        total = query.count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        rows = (
            query.order_by(AuditLog.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def count_actions(tenant_id: str, action: str, start, end, user_id: str | None = None) -> int:
        query = db.session.query(func.count(AuditLog.id)).filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.action == action,
            AuditLog.is_deleted.is_(False),
            AuditLog.created_at >= start,
            AuditLog.created_at < end,
        )
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        return int(query.scalar() or 0)

    @staticmethod
    def cancel_counts_by_user(tenant_id: str, start, end) -> list[tuple[str, str, int]]:
        rows = (
            db.session.query(
                AuditLog.user_id,
                AuditLog.user_name,
                func.count(AuditLog.id),
            )
            .filter(
                AuditLog.tenant_id == tenant_id,
                AuditLog.action == "CANCEL_BILL",
                AuditLog.is_deleted.is_(False),
                AuditLog.created_at >= start,
                AuditLog.created_at < end,
            )
            .group_by(AuditLog.user_id, AuditLog.user_name)
            .having(func.count(AuditLog.id) >= 2)
            .order_by(func.count(AuditLog.id).desc())
            .all()
        )
        return [(r[0], r[1] or "Unknown", int(r[2])) for r in rows]

    @staticmethod
    def recent_actions(tenant_id: str, actions: list[str], start, end, limit: int = 20):
        return (
            db.session.query(AuditLog)
            .filter(
                AuditLog.tenant_id == tenant_id,
                AuditLog.action.in_(actions),
                AuditLog.is_deleted.is_(False),
                AuditLog.created_at >= start,
                AuditLog.created_at < end,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
