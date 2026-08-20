"""Platform audit log data access (Master Admin)."""

from app.extensions import db
from app.models.platform_audit_log import PlatformAuditLog


class PlatformAuditRepository:
    @staticmethod
    def add(row: PlatformAuditLog) -> PlatformAuditLog:
        db.session.add(row)
        return row

    @staticmethod
    def list_filtered(
        *,
        action: str | None = None,
        entity_type: str | None = None,
        tenant_id: str | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> tuple[list[PlatformAuditLog], int]:
        query = db.session.query(PlatformAuditLog)
        if action:
            query = query.filter(PlatformAuditLog.action == action)
        if entity_type:
            query = query.filter(PlatformAuditLog.entity_type == entity_type)
        if tenant_id:
            query = query.filter(PlatformAuditLog.tenant_id == tenant_id)
        total = query.order_by(None).count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 25), 1), 100)
        rows = (
            query.order_by(PlatformAuditLog.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total
