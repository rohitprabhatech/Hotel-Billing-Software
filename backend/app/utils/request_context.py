"""Authenticated request context stored on flask.g."""

from dataclasses import dataclass

from flask import g


@dataclass
class RequestContext:
    user_id: str
    tenant_id: str
    role: str
    user_name: str
    email: str
    ip_address: str | None = None
    user_agent: str | None = None
    business_type: str | None = None


@dataclass
class MasterContext:
    admin_id: str
    role: str
    name: str
    email: str
    ip_address: str | None = None
    user_agent: str | None = None


def set_request_context(ctx: RequestContext) -> None:
    g.request_context = ctx


def get_request_context() -> RequestContext | None:
    return getattr(g, "request_context", None)


def require_request_context() -> RequestContext:
    ctx = get_request_context()
    if ctx is None:
        from app.utils.exceptions import UnauthorizedError

        raise UnauthorizedError("Authentication required")
    return ctx


def set_master_context(ctx: MasterContext) -> None:
    g.master_context = ctx


def get_master_context() -> MasterContext | None:
    return getattr(g, "master_context", None)


def require_master_context() -> MasterContext:
    ctx = get_master_context()
    if ctx is None:
        from app.utils.exceptions import ForbiddenError

        raise ForbiddenError("Master admin authorization required")
    return ctx