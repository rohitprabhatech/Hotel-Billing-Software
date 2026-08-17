"""Owner AI business assistant routes."""

from flask import Blueprint

from app.controllers import ai_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_OWNER

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.get("/analysis")
@roles_required(ROLE_OWNER)
def analyze():
    return ai_controller.analyze()


@ai_bp.get("/decisions")
@roles_required(ROLE_OWNER)
def decisions():
    return ai_controller.decisions()
