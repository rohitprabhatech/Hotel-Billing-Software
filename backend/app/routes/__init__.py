"""API blueprint registration."""

from flask import Blueprint

from app.routes.health_routes import health_bp


def register_blueprints(app):
    api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")
    api_v1.register_blueprint(health_bp)
    app.register_blueprint(api_v1)