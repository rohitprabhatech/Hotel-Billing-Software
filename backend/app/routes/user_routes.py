"""User management routes (OWNER only)."""

from flask import Blueprint

from app.controllers import user_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_OWNER

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("")
@roles_required(ROLE_OWNER)
def list_users():
    return user_controller.list_users()


@users_bp.post("")
@roles_required(ROLE_OWNER)
def create_user():
    return user_controller.create_user()


@users_bp.get("/<user_id>")
@roles_required(ROLE_OWNER)
def get_user(user_id):
    return user_controller.get_user(user_id)


@users_bp.put("/<user_id>")
@roles_required(ROLE_OWNER)
def update_user(user_id):
    return user_controller.update_user(user_id)


@users_bp.patch("/<user_id>/password")
@roles_required(ROLE_OWNER)
def reset_password(user_id):
    return user_controller.reset_password(user_id)