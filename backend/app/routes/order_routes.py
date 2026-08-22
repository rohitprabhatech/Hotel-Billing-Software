"""Restaurant order routes (BIZ-13)."""

from flask import Blueprint

from app.constants.permissions import PERM_ORDERS_READ, PERM_ORDERS_WRITE
from app.constants.permissions import PERM_BILLING, PERM_KOT_WRITE
from app.controllers import kot_controller, order_controller, order_settlement_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@orders_bp.get("")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_READ)
def list_orders():
    return order_controller.list_orders()


@orders_bp.post("")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_WRITE)
def create_order():
    return order_controller.create_order()


@orders_bp.get("/<order_id>")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_READ)
def get_order(order_id):
    return order_controller.get_order(order_id)


@orders_bp.patch("/<order_id>")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_WRITE)
def update_order(order_id):
    return order_controller.update_order(order_id)


@orders_bp.post("/<order_id>/cancel")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_WRITE)
def cancel_order(order_id):
    return order_controller.cancel_order(order_id)


@orders_bp.post("/<order_id>/items")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_WRITE)
def add_order_item(order_id):
    return order_controller.add_order_item(order_id)


@orders_bp.patch("/<order_id>/items/<line_id>")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_WRITE)
def update_order_item(order_id, line_id):
    return order_controller.update_order_item(order_id, line_id)


@orders_bp.delete("/<order_id>/items/<line_id>")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_ORDERS_WRITE)
def remove_order_item(order_id, line_id):
    return order_controller.remove_order_item(order_id, line_id)


@orders_bp.post("/<order_id>/kot")
@roles_required(*_STAFF)
@module_required("kot")
@permission_required(PERM_KOT_WRITE)
def fire_kot_for_order(order_id):
    return kot_controller.fire_kot_for_order(order_id)


@orders_bp.post("/<order_id>/settle")
@roles_required(*_STAFF)
@module_required("order_channels")
@permission_required(PERM_BILLING)
def settle_order(order_id):
    return order_settlement_controller.settle_order(order_id)
