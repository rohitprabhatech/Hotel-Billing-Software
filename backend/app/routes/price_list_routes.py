"""Price list routes (BIZ-51)."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.controllers import price_list_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

price_lists_bp = Blueprint("price_lists", __name__, url_prefix="/price-lists")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
# items.write is Owner-only in ROLE_PERMISSIONS (BIZ-03 / BIZ-65).
_WRITE = (ROLE_OWNER,)


@price_lists_bp.get("")
@roles_required(*_READ)
@module_required("price_lists")
@permission_required(PERM_ITEMS_READ)
def list_price_lists():
    return price_list_controller.list_price_lists()


@price_lists_bp.post("")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def create_price_list():
    return price_list_controller.create_price_list()


@price_lists_bp.get("/customer-assignments")
@roles_required(*_READ)
@module_required("price_lists")
@permission_required(PERM_ITEMS_READ)
def list_customer_assignments():
    return price_list_controller.list_customer_assignments()


@price_lists_bp.get("/<price_list_id>")
@roles_required(*_READ)
@module_required("price_lists")
@permission_required(PERM_ITEMS_READ)
def get_price_list(price_list_id):
    return price_list_controller.get_price_list(price_list_id)


@price_lists_bp.patch("/<price_list_id>")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def update_price_list(price_list_id):
    return price_list_controller.update_price_list(price_list_id)


@price_lists_bp.delete("/<price_list_id>")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def delete_price_list(price_list_id):
    return price_list_controller.delete_price_list(price_list_id)


@price_lists_bp.put("/<price_list_id>/items")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def replace_price_list_items(price_list_id):
    return price_list_controller.replace_price_list_items(price_list_id)


@price_lists_bp.put("/customer-assignments/<customer_id>")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def assign_customer_price_list(customer_id):
    return price_list_controller.assign_customer_price_list(customer_id)


@price_lists_bp.delete("/customer-assignments/<customer_id>")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def unassign_customer_price_list(customer_id):
    return price_list_controller.unassign_customer_price_list(customer_id)
