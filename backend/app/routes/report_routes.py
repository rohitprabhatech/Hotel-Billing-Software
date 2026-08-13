"""Owner report routes."""

from flask import Blueprint

from app.controllers import report_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_OWNER

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.get("/summary")
@roles_required(ROLE_OWNER)
def summary():
    return report_controller.summary()


@reports_bp.get("/daily-sales")
@roles_required(ROLE_OWNER)
def daily_sales():
    return report_controller.daily_sales()


@reports_bp.get("/monthly-sales")
@roles_required(ROLE_OWNER)
def monthly_sales():
    return report_controller.monthly_sales()


@reports_bp.get("/custom-sales")
@roles_required(ROLE_OWNER)
def custom_sales():
    return report_controller.custom_sales()


@reports_bp.get("/export")
@roles_required(ROLE_OWNER)
def export_report():
    return report_controller.export_report()