"""Purchase order routes (BIZ-52)."""

from flask import Blueprint

from app.constants.permissions import PERM_PURCHASES_READ, PERM_PURCHASES_WRITE
from app.controllers import purchase_order_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

purchase_orders_bp = Blueprint("purchase_orders", __name__, url_prefix="/purchase-orders")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@purchase_orders_bp.get("")
@roles_required(*_READ)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_READ)
def list_purchase_orders():
    return purchase_order_controller.list_purchase_orders()


@purchase_orders_bp.post("")
@roles_required(*_WRITE)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_WRITE)
def create_purchase_order():
    return purchase_order_controller.create_purchase_order()


@purchase_orders_bp.get("/<order_id>")
@roles_required(*_READ)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_READ)
def get_purchase_order(order_id):
    return purchase_order_controller.get_purchase_order(order_id)


@purchase_orders_bp.patch("/<order_id>/status")
@roles_required(*_WRITE)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_WRITE)
def update_purchase_order_status(order_id):
    return purchase_order_controller.update_purchase_order_status(order_id)


@purchase_orders_bp.post("/<order_id>/convert")
@roles_required(*_WRITE)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_WRITE)
def convert_purchase_order(order_id):
    return purchase_order_controller.convert_purchase_order(order_id)
