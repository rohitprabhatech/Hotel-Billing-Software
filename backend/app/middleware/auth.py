"""JWT authentication and role authorization decorators."""

from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.models.role import VALID_ROLES
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import ForbiddenError, UnauthorizedError
from app.utils.request_context import RequestContext, set_request_context


def _client_meta():
    from flask import current_app

    if current_app.config.get("TRUST_PROXY_HEADERS"):
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()
    else:
        # Prefer direct peer address unless reverse-proxy trust is enabled.
        ip = request.remote_addr
    ua = request.headers.get("User-Agent")
    return ip, ua


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as exc:
            raise UnauthorizedError("Invalid or missing authentication token") from exc

        identity = get_jwt_identity()
        claims = get_jwt()
        claim_tenant_id = claims.get("tenant_id")
        claim_role = claims.get("role")

        if not identity or not claim_tenant_id or claim_role not in VALID_ROLES:
            raise UnauthorizedError("Invalid authentication token claims")

        user = UserRepository.get_by_id(identity)
        if user is None or not user.is_active:
            raise UnauthorizedError("User is inactive or not found")

        if user.tenant_id != claim_tenant_id:
            raise UnauthorizedError("Tenant mismatch in authentication token")

        if not user.tenant or not user.tenant.is_active():
            raise UnauthorizedError("Tenant is suspended")

        if user.role_name != claim_role:
            raise UnauthorizedError("Role mismatch in authentication token")

        claim_tv = claims.get("tv", 0)
        if int(claim_tv or 0) != int(user.token_version or 0):
            raise UnauthorizedError("Session expired. Please sign in again.")

        ip, ua = _client_meta()
        set_request_context(
            RequestContext(
                user_id=user.id,
                tenant_id=user.tenant_id,
                role=user.role_name,
                user_name=user.name,
                email=user.email,
                ip_address=ip,
                user_agent=ua,
            )
        )
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*roles: str):
    allowed = set(roles)

    def decorator(fn):
        @wraps(fn)
        @auth_required
        def wrapper(*args, **kwargs):
            from app.utils.request_context import require_request_context

            ctx = require_request_context()
            if ctx.role not in allowed:
                raise ForbiddenError("You do not have permission to perform this action")
            return fn(*args, **kwargs)

        return wrapper

    return decorator