"""Public anonymous routes for the landing page."""

from flask import Blueprint

from app.controllers import public_controller

public_bp = Blueprint("public", __name__, url_prefix="/public")


@public_bp.get("/plans")
def list_public_plans():
    return public_controller.list_public_plans()
