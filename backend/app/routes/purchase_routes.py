"""Purchase routes (BIZ-06)."""

from flask import Blueprint

from app.constants.permissions import PERM_PURCHASES_READ, PERM_PURCHASES_WRITE
from app.controllers import purchase_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_MANAGER, ROLE_OWNER
from app.utils.permission_access import permission_required

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")

_OPS = (ROLE_OWNER, ROLE_MANAGER)


@purchases_bp.get("")
@roles_required(*_OPS)
@permission_required(PERM_PURCHASES_READ)
def list_purchases():
    return purchase_controller.list_purchases()


@purchases_bp.post("")
@roles_required(*_OPS)
@permission_required(PERM_PURCHASES_WRITE)
def create_purchase():
    return purchase_controller.create_purchase()


@purchases_bp.get("/<purchase_id>")
@roles_required(*_OPS)
@permission_required(PERM_PURCHASES_READ)
def get_purchase(purchase_id):
    return purchase_controller.get_purchase(purchase_id)


@purchases_bp.post("/<purchase_id>/cancel")
@roles_required(*_OPS)
@permission_required(PERM_PURCHASES_WRITE)
def cancel_purchase(purchase_id):
    return purchase_controller.cancel_purchase(purchase_id)
