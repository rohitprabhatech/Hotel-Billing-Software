"""Tenant profile controller."""

from flask import request

from app.models.role import ROLE_OWNER
from app.schemas.billing_settings_schemas import billing_settings_schema
from app.schemas.tenant_schemas import update_tenant_schema
from app.services.tenant_service import TenantService
from app.utils.request_context import require_request_context
from app.utils.responses import success_response


def list_business_types():
    return success_response(data=TenantService.list_business_types())


def get_my_modules():
    from app.services.module_service import ModuleService

    return success_response(data=ModuleService.resolve_for_current_tenant())


def get_my_tenant():
    ctx = require_request_context()
    full = ctx.role == ROLE_OWNER
    return success_response(data=TenantService.get_my_tenant(full=full))


def update_my_tenant():
    raw = request.get_json() or {}
    payload = update_tenant_schema.load(raw)
    clean = {key: payload[key] for key in raw.keys() if key in payload}
    data = TenantService.update_my_tenant(clean)
    return success_response(data=data)


def get_billing_settings():
    return success_response(data=TenantService.get_billing_settings())


def update_billing_settings():
    raw = request.get_json() or {}
    payload = billing_settings_schema.load(raw)
    data = TenantService.update_billing_settings(payload)
    return success_response(data=data)
