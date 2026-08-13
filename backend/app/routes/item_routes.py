"""Item routes."""

from flask import Blueprint

from app.controllers import item_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER

items_bp = Blueprint("items", __name__, url_prefix="/items")


@items_bp.get("")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def list_items():
    return item_controller.list_items()


@items_bp.post("")
@roles_required(ROLE_OWNER)
def create_item():
    return item_controller.create_item()


@items_bp.get("/<item_id>")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def get_item(item_id):
    return item_controller.get_item(item_id)


@items_bp.put("/<item_id>")
@roles_required(ROLE_OWNER)
def update_item(item_id):
    return item_controller.update_item(item_id)


@items_bp.patch("/<item_id>/status")
@roles_required(ROLE_OWNER)
def set_item_status(item_id):
    return item_controller.set_item_status(item_id)