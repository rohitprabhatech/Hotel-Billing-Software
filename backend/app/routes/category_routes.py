"""Category routes."""

from flask import Blueprint

from app.controllers import category_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.get("")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def list_categories():
    return category_controller.list_categories()


@categories_bp.post("")
@roles_required(ROLE_OWNER)
def create_category():
    return category_controller.create_category()


@categories_bp.get("/<category_id>")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def get_category(category_id):
    return category_controller.get_category(category_id)


@categories_bp.put("/<category_id>")
@roles_required(ROLE_OWNER)
def update_category(category_id):
    return category_controller.update_category(category_id)


@categories_bp.patch("/<category_id>/status")
@roles_required(ROLE_OWNER)
def set_category_status(category_id):
    return category_controller.set_category_status(category_id)