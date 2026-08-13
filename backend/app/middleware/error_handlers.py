"""Centralized Flask error handlers."""

from flask import current_app
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import HTTPException

from app.utils.exceptions import AppError
from app.utils.responses import error_response


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        return error_response(
            message=exc.message,
            code=exc.code,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(exc: MarshmallowValidationError):
        return error_response(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=400,
            details=exc.messages,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        return error_response(
            message=exc.description or "Request error",
            code=exc.name.replace(" ", "_").upper() if exc.name else "HTTP_ERROR",
            status_code=exc.code or 400,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception):
        current_app.logger.exception("Unhandled exception: %s", exc)
        return error_response(
            message="An unexpected error occurred",
            code="INTERNAL_SERVER_ERROR",
            status_code=500,
        )