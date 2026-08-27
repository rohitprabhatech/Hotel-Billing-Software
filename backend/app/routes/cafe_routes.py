"""Cafe quick POS routes (BIZ-17) + cafe dashboard (Sprint 4)."""

from flask import Blueprint

from app.constants.permissions import PERM_ADDONS_READ, PERM_REPORTS
from app.controllers import cafe_offer_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

cafe_bp = Blueprint("cafe", __name__, url_prefix="/cafe")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_OPS = (ROLE_OWNER, ROLE_MANAGER)


@cafe_bp.get("/pos-catalog")
@roles_required(*_STAFF)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_READ)
def quick_pos_catalog():
    return cafe_offer_controller.quick_pos_catalog()


@cafe_bp.get("/dashboard")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_REPORTS)
def cafe_dashboard():
    return cafe_offer_controller.cafe_dashboard()
