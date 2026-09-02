"""Owner-only destructive / sensitive operations."""

from app.models.role import ROLE_OWNER
from app.utils.exceptions import ForbiddenError
from app.utils.request_context import require_request_context


def require_owner():
    ctx = require_request_context()
    if ctx.role != ROLE_OWNER:
        raise ForbiddenError("Only the owner can perform this action")
    return ctx
