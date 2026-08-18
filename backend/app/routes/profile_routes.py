"""Authenticated profile routes."""

from flask import Blueprint

from app.controllers import profile_controller
from app.middleware.auth import auth_required

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.get("")
@auth_required(require_subscription=False)
def get_profile():
    return profile_controller.get_profile()


@profile_bp.put("")
@auth_required(require_subscription=False)
def update_profile():
    return profile_controller.update_profile()


@profile_bp.post("/request-email-change")
@auth_required(require_subscription=False)
def request_email_change():
    return profile_controller.request_email_change()
