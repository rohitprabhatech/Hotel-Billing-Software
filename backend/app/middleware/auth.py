"""JWT authentication and role authorization decorators."""

from functools import wraps

from flask import g, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.models.master_admin import ROLE_MASTER_ADMIN
from app.models.role import VALID_ROLES
from app.repositories.master_admin_repository import MasterAdminRepository
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import ForbiddenError, UnauthorizedError
from app.utils.request_context import (
    MasterContext,
    RequestContext,
    set_master_context,
    set_request_context,
)


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


def _bind_identity() -> str:
    """Verify JWT and bind tenant or master context. Returns 'tenant' | 'master'."""
    try:
        verify_jwt_in_request()
    except Exception as exc:
        raise UnauthorizedError("Invalid or missing authentication token") from exc

    identity = get_jwt_identity()
    claims = get_jwt()
    claim_role = claims.get("role")
    ip, ua = _client_meta()

    g.master_context = None
    g.request_context = None

    if claim_role == ROLE_MASTER_ADMIN:
        if not identity:
            raise UnauthorizedError("Invalid authentication token claims")
        admin = MasterAdminRepository.get_by_id(identity)
        if admin is None or not admin.is_active:
            raise UnauthorizedError("User is inactive or not found")
        claim_tv = claims.get("tv", 0)
        if int(claim_tv or 0) != int(admin.token_version or 0):
            raise UnauthorizedError("Session expired. Please sign in again.")
        set_master_context(
            MasterContext(
                admin_id=admin.id,
                role=ROLE_MASTER_ADMIN,
                name=admin.name,
                email=admin.email,
                ip_address=ip,
                user_agent=ua,
            )
        )
        return "master"

    claim_tenant_id = claims.get("tenant_id")
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
    return "tenant"


def session_required(fn):
    """Tenant Owner/Billing User or Master Admin."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        _bind_identity()
        return fn(*args, **kwargs)

    return wrapper


def auth_required(fn=None, *, require_subscription=True):
    """Business tenant APIs only — Master Admin is rejected with 403."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kind = _bind_identity()
            if kind == "master":
                raise ForbiddenError("Master admin cannot access tenant APIs")
            if require_subscription:
                from app.services.subscription_service import SubscriptionService

                SubscriptionService.enforce_access()
            return func(*args, **kwargs)

        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator


def master_required(fn):
    """Platform Master Admin APIs only — business users are rejected with 403."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        kind = _bind_identity()
        if kind != "master":
            raise ForbiddenError("Master admin authorization required")
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
