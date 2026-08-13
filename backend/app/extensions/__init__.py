"""Flask extensions initialized in the app factory."""

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(_reason):
        from app.utils.responses import error_response

        return error_response(
            message="Invalid authentication token",
            code="UNAUTHORIZED",
            status_code=401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(_reason):
        from app.utils.responses import error_response

        return error_response(
            message="Authentication required",
            code="UNAUTHORIZED",
            status_code=401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        from app.utils.responses import error_response

        return error_response(
            message="Authentication token has expired",
            code="UNAUTHORIZED",
            status_code=401,
        )