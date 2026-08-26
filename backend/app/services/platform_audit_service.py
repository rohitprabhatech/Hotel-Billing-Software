"""Master Admin platform audit logging — never stores secrets."""

from app.models.platform_audit_log import PlatformAuditLog
from app.repositories.platform_audit_repository import PlatformAuditRepository
from app.utils.audit_scrub import scrub_audit_payload
from app.utils.ids import new_uuid
from app.utils.request_context import get_master_context


class PlatformAuditService:
    @staticmethod
    def log(
        *,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        tenant_id: str | None = None,
        old_data: dict | None = None,
        new_data: dict | None = None,
    ) -> PlatformAuditLog:
        ctx = get_master_context()
        row = PlatformAuditLog(
            id=new_uuid(),
            actor_id=ctx.admin_id if ctx else None,
            actor_name=ctx.name if ctx else None,
            actor_email=ctx.email if ctx else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            tenant_id=tenant_id,
            old_data=scrub_audit_payload(old_data) if old_data else None,
            new_data=scrub_audit_payload(new_data) if new_data else None,
            ip_address=ctx.ip_address if ctx else None,
            user_agent=ctx.user_agent if ctx else None,
        )
        PlatformAuditRepository.add(row)
        return row

    @staticmethod
    def list_logs(*, action=None, entity_type=None, tenant_id=None, page=1, per_page=25):
        from app.utils.request_context import require_master_context

        require_master_context()
        rows, total = PlatformAuditRepository.list_filtered(
            action=(str(action).strip().upper() if action else None),
            entity_type=(str(entity_type).strip().upper() if entity_type else None),
            tenant_id=tenant_id,
            page=page,
            per_page=per_page,
        )
        return (
            [PlatformAuditService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 25), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def serialize(row: PlatformAuditLog) -> dict:
        return {
            "id": row.id,
            "actor_id": row.actor_id,
            "actor_name": row.actor_name,
            "actor_email": row.actor_email,
            "action": row.action,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "tenant_id": row.tenant_id,
            "old_data": row.old_data,
            "new_data": row.new_data,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
