"""Health routes."""

from flask import Blueprint

from app.controllers import health_controller

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return health_controller.get_health()


@health_bp.get("/health/ready")
def ready():
    return health_controller.get_readiness()