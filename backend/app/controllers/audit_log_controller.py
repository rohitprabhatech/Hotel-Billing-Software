"""Audit log HTTP controller."""

from flask import request

from app.services.audit_log_service import AuditLogService
from app.utils.responses import success_response


def list_logs():
    data, meta = AuditLogService.list_logs(
        user_id=request.args.get("user_id"),
        action=request.args.get("action"),
        entity_type=request.args.get("entity_type"),
        entity_id=request.args.get("entity_id"),
        bill_number=request.args.get("bill_number"),
        q=request.args.get("q"),
        from_date=request.args.get("from"),
        to_date=request.args.get("to"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def get_log(log_id: str):
    return success_response(data=AuditLogService.get_log(log_id))


def alerts():
    return success_response(data=AuditLogService.alerts())