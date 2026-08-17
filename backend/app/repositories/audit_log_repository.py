"""Tenant-scoped audit log queries (read-only)."""

from datetime import datetime

from sqlalchemy import func, or_

from app.extensions import db
from app.models.audit_log import AuditLog
from app.models.bill import Bill


class AuditLogRepository:
    @staticmethod
    def get_by_id_and_tenant(log_id: str, tenant_id: str) -> AuditLog | None:
        return (
            db.session.query(AuditLog)
            .filter(AuditLog.id == log_id, AuditLog.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        user_id: str | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        bill_number: str | None = None,
        q: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[AuditLog], int]:
        query = db.session.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if entity_type:
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
                AuditLog.created_at >= start,
                AuditLog.created_at < end,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
