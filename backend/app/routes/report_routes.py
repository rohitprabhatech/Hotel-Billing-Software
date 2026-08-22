"""Owner and manager report routes."""

from flask import Blueprint

from app.constants.permissions import PERM_REPORTS
from app.controllers import report_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.get("/summary")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_REPORTS)
def summary():
    return report_controller.summary()


@reports_bp.get("/daily-sales")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_REPORTS)
def daily_sales():
    return report_controller.daily_sales()


@reports_bp.get("/weekly-sales")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_REPORTS)
def weekly_sales():
    return report_controller.weekly_sales()


@reports_bp.get("/monthly-sales")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_REPORTS)
def monthly_sales():
    return report_controller.monthly_sales()


@reports_bp.get("/custom-sales")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_REPORTS)
def custom_sales():
    return report_controller.custom_sales()


@reports_bp.get("/fb")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@module_required("order_channels")
@permission_required(PERM_REPORTS)
def fb_report():
    return report_controller.fb_report()


@reports_bp.get("/export")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_REPORTS)
def export_report():
    return report_controller.export_report()
