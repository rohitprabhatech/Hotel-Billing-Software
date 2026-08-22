"""Grocery fast POS routes (BIZ-20)."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ
from app.controllers import grocery_pos_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

grocery_bp = Blueprint("grocery", __name__, url_prefix="/grocery")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@grocery_bp.get("/pos-catalog")
@roles_required(*_STAFF)
@module_required("barcode_pos")
@permission_required(PERM_ITEMS_READ)
def pos_catalog():
    return grocery_pos_controller.pos_catalog()
