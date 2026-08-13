"""Domain exceptions mapped to HTTP responses."""


class AppError(Exception):
    status_code = 400
    code = "APP_ERROR"

    def __init__(self, message: str, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"