"""Flask application factory."""

from flask import Flask

from app.config.settings import get_config
from app.extensions import init_extensions
from app.middleware.error_handlers import register_error_handlers
from app.routes import register_blueprints


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    init_extensions(app)
    register_error_handlers(app)
    register_blueprints(app)

    # Import models so Flask-Migrate can detect metadata.
    from app import models  # noqa: F401

    @app.get("/")
    def root():
        from app.utils.responses import success_response

        return success_response(
            data={
                "name": "Business Billing API",
                "api_base": "/api/v1",
            }
        )

    return app