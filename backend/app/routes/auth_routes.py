"""Auth routes."""

from flask import Blueprint

from app.controllers import auth_controller
from app.extensions import limiter
from app.middleware.auth import auth_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
@limiter.limit("20 per minute")
def login():
    return auth_controller.login()


@auth_bp.post("/logout")
@auth_required
def logout():
    return auth_controller.logout()


@auth_bp.get("/me")
@auth_required
def me():
    return auth_controller.me()