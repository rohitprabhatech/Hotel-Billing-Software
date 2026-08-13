"""Tenant profile routes."""

from flask import Blueprint

from app.controllers import tenant_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER

tenants_bp = Blueprint("tenants", __name__, url_prefix="/tenants")


@tenants_bp.get("/me")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def get_my_tenant():
    return tenant_controller.get_my_tenant()


@tenants_bp.put("/me")
@roles_required(ROLE_OWNER)
def update_my_tenant():
    return tenant_controller.update_my_tenant()