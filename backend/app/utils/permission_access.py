"""Permission checks for tenant roles (BIZ-03)."""

from functools import wraps

from app.constants.permissions import has_any_permission, has_permission
from app.utils.exceptions import ForbiddenError
from app.utils.request_context import require_request_context


def require_permission(permission: str) -> None:
    ctx = require_request_context()
    if not has_permission(ctx.role, permission, ctx.business_type):
        raise ForbiddenError("You do not have permission to perform this action")


def require_any_permission(*permissions: str) -> None:
    ctx = require_request_context()
    if not has_any_permission(ctx.role, *permissions, business_type=ctx.business_type):
        raise ForbiddenError("You do not have permission to perform this action")


def permission_required(*permissions: str):
    """Use after ``@roles_required`` / ``@auth_required`` (request context must exist)."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            require_any_permission(*permissions)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
