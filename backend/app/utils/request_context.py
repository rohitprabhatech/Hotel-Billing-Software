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