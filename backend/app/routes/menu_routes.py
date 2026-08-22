"""Restaurant menu routes (BIZ-11)."""

from flask import Blueprint

from app.constants.permissions import PERM_ADDONS_READ, PERM_ADDONS_WRITE
from app.controllers import cafe_offer_controller, menu_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_OPS = (ROLE_OWNER, ROLE_MANAGER)


@menu_bp.get("")
@roles_required(*_STAFF)
@module_required("restaurant_menu")
def list_menu():
    return menu_controller.list_menu()


@menu_bp.get("/addons")
@roles_required(*_STAFF)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_READ)
def list_addons():
    return cafe_offer_controller.list_addons()


@menu_bp.post("/addons")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_WRITE)
def create_addon_group():
    return cafe_offer_controller.create_addon_group()


@menu_bp.delete("/addons/<group_id>")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_WRITE)
def delete_addon_group(group_id):
    return cafe_offer_controller.delete_addon_group(group_id)
