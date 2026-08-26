"""Sales order routes (BIZ-52)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import sales_order_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

sales_orders_bp = Blueprint("sales_orders", __name__, url_prefix="/sales-orders")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@sales_orders_bp.get("")
@roles_required(*_READ)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def list_sales_orders():
    return sales_order_controller.list_sales_orders()


@sales_orders_bp.post("")
@roles_required(*_WRITE)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def create_sales_order():
    return sales_order_controller.create_sales_order()


@sales_orders_bp.get("/<order_id>")
@roles_required(*_READ)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def get_sales_order(order_id):
    return sales_order_controller.get_sales_order(order_id)


@sales_orders_bp.patch("/<order_id>/status")
@roles_required(*_WRITE)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def update_sales_order_status(order_id):
    return sales_order_controller.update_sales_order_status(order_id)


@sales_orders_bp.post("/<order_id>/convert")
@roles_required(*_WRITE)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def convert_sales_order(order_id):
    return sales_order_controller.convert_sales_order(order_id)
