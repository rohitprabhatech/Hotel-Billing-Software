"""Combo routes (BIZ-17)."""

from flask import Blueprint

from app.constants.permissions import PERM_ADDONS_READ, PERM_ADDONS_WRITE
from app.controllers import cafe_offer_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

combos_bp = Blueprint("combos", __name__, url_prefix="/combos")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_OPS = (ROLE_OWNER, ROLE_MANAGER)


@combos_bp.get("")
@roles_required(*_STAFF)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_READ)
def list_combos():
    return cafe_offer_controller.list_combos()


@combos_bp.post("")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_WRITE)
def create_combo():
    return cafe_offer_controller.create_combo()


@combos_bp.get("/<combo_id>")
@roles_required(*_STAFF)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_READ)
def get_combo(combo_id):
    return cafe_offer_controller.get_combo(combo_id)


@combos_bp.delete("/<combo_id>")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_WRITE)
def delete_combo(combo_id):
    return cafe_offer_controller.delete_combo(combo_id)
