"""Cafe quick POS routes (BIZ-17)."""

from flask import Blueprint

from app.constants.permissions import PERM_ADDONS_READ
from app.controllers import cafe_offer_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

cafe_bp = Blueprint("cafe", __name__, url_prefix="/cafe")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@cafe_bp.get("/pos-catalog")
@roles_required(*_STAFF)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_READ)
def quick_pos_catalog():
    return cafe_offer_controller.quick_pos_catalog()
