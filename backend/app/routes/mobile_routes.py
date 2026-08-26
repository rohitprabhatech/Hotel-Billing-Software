"""Mobile pack reports and customer history (BIZ-32)."""

from flask import Blueprint

from app.constants.permissions import PERM_CUSTOMERS_READ, PERM_REPORTS
from app.controllers import mobile_report_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

mobile_bp = Blueprint("mobile", __name__, url_prefix="/mobile")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@mobile_bp.get("/sales")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@module_required("serial_imei")
@permission_required(PERM_REPORTS)
def mobile_sales():
    return mobile_report_controller.sales_report()


@mobile_bp.get("/customer-history")
@roles_required(*_STAFF)
@module_required("serial_imei")
@permission_required(PERM_CUSTOMERS_READ)
def mobile_customer_history():
    return mobile_report_controller.customer_history()
