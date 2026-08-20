"""Module feature-gate decorator (BIZ-02).

Use with ``@roles_required`` / ``@auth_required`` so JWT context is already bound:

    @roles_required(ROLE_OWNER, ROLE_BILLING_USER)
    @module_required("table_management")
    def list_tables():
        ...
"""

from functools import wraps

from app.repositories.tenant_repository import TenantRepository
from app.services.module_service import ModuleService
from app.utils.exceptions import NotFoundError
from app.utils.request_context import require_request_context


def module_required(module_code: str):
    """Require that ``module_code`` is enabled for the current tenant."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ctx = require_request_context()
            tenant = TenantRepository.get_by_id(ctx.tenant_id)
            if tenant is None:
                raise NotFoundError("Tenant not found")
            ModuleService.require_enabled(tenant, module_code)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
