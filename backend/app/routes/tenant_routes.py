"""Tenant profile routes."""

from flask import Blueprint

from app.controllers import tenant_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER

tenants_bp = Blueprint("tenants", __name__, url_prefix="/tenants")


@tenants_bp.get("/business-types")
def list_business_types():
    return tenant_controller.list_business_types()


@tenants_bp.get("/me")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def get_my_tenant():
    return tenant_controller.get_my_tenant()


@tenants_bp.put("/me")
@roles_required(ROLE_OWNER)
def update_my_tenant():
    return tenant_controller.update_my_tenant()


@tenants_bp.get("/me/whatsapp")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def get_whatsapp_config():
    from app.controllers import whatsapp_controller

    return whatsapp_controller.get_whatsapp_config()


@tenants_bp.put("/me/whatsapp")
@roles_required(ROLE_OWNER)
def save_whatsapp_config():
    from app.controllers import whatsapp_controller

    return whatsapp_controller.save_whatsapp_config()


@tenants_bp.post("/me/whatsapp/test")
@roles_required(ROLE_OWNER)
def test_whatsapp_config():
    from app.controllers import whatsapp_controller

    return whatsapp_controller.test_whatsapp_config()


@tenants_bp.post("/me/whatsapp/disconnect")
@roles_required(ROLE_OWNER)
def disconnect_whatsapp_config():
    from app.controllers import whatsapp_controller

    return whatsapp_controller.disconnect_whatsapp_config()


@tenants_bp.post("/me/whatsapp/simulate-delivery-status")
@roles_required(ROLE_OWNER)
def simulate_whatsapp_delivery():
    from app.controllers import whatsapp_controller

    return whatsapp_controller.simulate_whatsapp_delivery()
