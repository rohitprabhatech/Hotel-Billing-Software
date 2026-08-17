"""Owner audit log routes — no delete endpoints."""

from flask import Blueprint

from app.controllers import audit_log_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_OWNER

audit_logs_bp = Blueprint("audit_logs", __name__, url_prefix="/audit-logs")


@audit_logs_bp.get("")
@roles_required(ROLE_OWNER)
def list_logs():
    return audit_log_controller.list_logs()


@audit_logs_bp.get("/alerts")
@roles_required(ROLE_OWNER)
def alerts():
    return audit_log_controller.alerts()


@audit_logs_bp.get("/<log_id>")
@roles_required(ROLE_OWNER)
def get_log(log_id):
    return audit_log_controller.get_log(log_id)