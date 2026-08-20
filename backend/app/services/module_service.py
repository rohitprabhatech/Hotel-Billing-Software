"""Resolve enabled modules for a tenant (BIZ-02)."""

from __future__ import annotations

from app.constants.business_types import business_type_label, coerce_business_type
from app.constants.modules import (
    defaults_for_business_type,
    list_module_catalog,
    module_label,
)
from app.repositories.tenant_repository import TenantRepository
from app.utils.exceptions import ForbiddenError, NotFoundError
from app.utils.request_context import require_request_context


class ModuleService:
    @staticmethod
    def enabled_codes_for_business_type(business_type: str | None) -> list[str]:
        return sorted(defaults_for_business_type(business_type))

    @staticmethod
    def enabled_codes_for_tenant(tenant) -> list[str]:
        return ModuleService.enabled_codes_for_business_type(tenant.business_type)

    @staticmethod
    def is_enabled_for_tenant(tenant, module_code: str) -> bool:
        code = (module_code or "").strip().lower()
        return code in defaults_for_business_type(tenant.business_type)

    @staticmethod
    def require_enabled(tenant, module_code: str) -> None:
        code = (module_code or "").strip().lower()
        if not ModuleService.is_enabled_for_tenant(tenant, code):
            raise ForbiddenError(
                f"Module '{code}' is not enabled for this business type.",
                details={
                    "module": code,
                    "business_type": coerce_business_type(tenant.business_type),
                },
            )

    @staticmethod
    def resolve_for_current_tenant() -> dict:
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        business_type = coerce_business_type(tenant.business_type)
        enabled = ModuleService.enabled_codes_for_tenant(tenant)
        enabled_set = set(enabled)
        modules = [
            {
                "code": row["code"],
                "label": row["label"],
                "is_core": row["is_core"],
                "enabled": row["code"] in enabled_set,
            }
            for row in list_module_catalog()
        ]
        return {
            "business_type": business_type,
            "business_type_label": business_type_label(business_type),
            "enabled_modules": enabled,
            "modules": modules,
            "overrides": [],  # reserved — tenant overrides not used in BIZ-02
        }

    @staticmethod
    def serialize_enabled_summary(tenant) -> dict:
        enabled = ModuleService.enabled_codes_for_tenant(tenant)
        return {
            "enabled_modules": enabled,
            "enabled_module_labels": {code: module_label(code) for code in enabled},
        }
