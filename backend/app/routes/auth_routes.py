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


@auth_bp.post("/register-hotel")
@limiter.limit("10 per minute")
def register_hotel():
    return auth_controller.register_hotel()


@auth_bp.post("/verify-email")
@limiter.limit("20 per minute")
def verify_email():
    return auth_controller.verify_email()


@auth_bp.post("/resend-verification")
@limiter.limit("10 per minute")
def resend_verification():
    return auth_controller.resend_verification()


@auth_bp.post("/forgot-password")
@limiter.limit("10 per minute")
def forgot_password():
    return auth_controller.forgot_password()


@auth_bp.post("/reset-password")
@limiter.limit("10 per minute")
def reset_password():
    return auth_controller.reset_password()


@auth_bp.post("/change-password")
@auth_required
def change_password():
    return auth_controller.change_password()
