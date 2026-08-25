"""Clothing POS (BIZ-26) and reports (BIZ-28)."""

from flask import Blueprint

from app.constants.permissions import PERM_CUSTOMERS_READ, PERM_ITEMS_READ, PERM_REPORTS
from app.controllers import clothing_pos_controller, clothing_report_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

clothing_bp = Blueprint("clothing", __name__, url_prefix="/clothing")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@clothing_bp.get("/pos-catalog")
@roles_required(*_STAFF)
@module_required("variants")
@permission_required(PERM_ITEMS_READ)
def pos_catalog():
    return clothing_pos_controller.pos_catalog()


@clothing_bp.get("/sales")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@module_required("variants")
@permission_required(PERM_REPORTS)
def clothing_sales():
    return clothing_report_controller.sales_report()


@clothing_bp.get("/customer-history")
@roles_required(*_STAFF)
@module_required("variants")
@permission_required(PERM_CUSTOMERS_READ)
def clothing_customer_history():
    return clothing_report_controller.customer_history()
