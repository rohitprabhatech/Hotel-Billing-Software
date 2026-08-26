"""Audit logging service."""

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository
from app.utils.audit_scrub import scrub_audit_payload
from app.utils.ids import new_uuid
from app.utils.request_context import get_request_context


class AuditService:
    @staticmethod
    def log(
        *,
        tenant_id: str,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        old_data: dict | None = None,
        new_data: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        commit: bool = False,
    ) -> AuditLog:
        ctx = get_request_context()
        log = AuditLog(
            id=new_uuid(),
            tenant_id=tenant_id,
            user_id=user_id if user_id is not None else (ctx.user_id if ctx else None),
            user_name=user_name if user_name is not None else (ctx.user_name if ctx else None),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_data=scrub_audit_payload(old_data) if old_data is not None else None,
            new_data=scrub_audit_payload(new_data) if new_data is not None else None,
            ip_address=ip_address if ip_address is not None else (ctx.ip_address if ctx else None),
            user_agent=user_agent if user_agent is not None else (ctx.user_agent if ctx else None),
        )
        AuditRepository.add(log)
        if commit:
            AuditRepository.commit()
        return log
