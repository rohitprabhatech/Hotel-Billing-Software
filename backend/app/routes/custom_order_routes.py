"""Custom product order routes (BIZ-42)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import custom_order_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

custom_orders_bp = Blueprint("custom_orders", __name__, url_prefix="/custom-orders")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_MANAGE = (ROLE_OWNER, ROLE_MANAGER)


@custom_orders_bp.get("")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def list_orders():
    return custom_order_controller.list_orders()


@custom_orders_bp.post("")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def create_order():
    return custom_order_controller.create_order()


@custom_orders_bp.get("/<order_id>")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def get_order(order_id):
    return custom_order_controller.get_order(order_id)


@custom_orders_bp.patch("/<order_id>/status")
@roles_required(*_MANAGE)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def update_status(order_id):
    return custom_order_controller.update_status(order_id)


@custom_orders_bp.post("/<order_id>/advance")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def record_advance(order_id):
    return custom_order_controller.record_advance(order_id)
