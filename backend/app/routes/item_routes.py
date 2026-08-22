"""Item routes — tenant staff with permission matrix (BIZ-03)."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK, PERM_ITEMS_WRITE
from app.controllers import item_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.permission_access import permission_required

items_bp = Blueprint("items", __name__, url_prefix="/items")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@items_bp.get("")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_READ)
def list_items():
    return item_controller.list_items()


@items_bp.post("")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def create_item():
    return item_controller.create_item()


@items_bp.get("/by-barcode/<barcode>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_READ)
def get_item_by_barcode(barcode):
    return item_controller.get_item_by_barcode(barcode)


@items_bp.get("/<item_id>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_READ)
def get_item(item_id):
    return item_controller.get_item(item_id)


@items_bp.put("/<item_id>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def update_item(item_id):
    return item_controller.update_item(item_id)


@items_bp.patch("/<item_id>/status")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def set_item_status(item_id):
    return item_controller.set_item_status(item_id)


@items_bp.post("/<item_id>/adjust-stock")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_STOCK)
def adjust_stock(item_id):
    return item_controller.adjust_stock(item_id)


@items_bp.post("/<item_id>/receive-stock")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_STOCK)
def receive_stock(item_id):
    return item_controller.receive_stock(item_id)


@items_bp.delete("/<item_id>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def delete_item(item_id):
    """Hard delete is intentionally unsupported — returns 405 via controller."""
    return item_controller.delete_item(item_id)
