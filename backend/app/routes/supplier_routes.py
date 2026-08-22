"""Supplier master routes (BIZ-05)."""

from flask import Blueprint

from app.constants.permissions import PERM_SUPPLIERS_READ, PERM_SUPPLIERS_WRITE
from app.controllers import supplier_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.permission_access import permission_required

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@suppliers_bp.get("")
@roles_required(*_STAFF)
@permission_required(PERM_SUPPLIERS_READ)
def list_suppliers():
    return supplier_controller.list_suppliers()


@suppliers_bp.post("")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_SUPPLIERS_WRITE)
def create_supplier():
    return supplier_controller.create_supplier()


@suppliers_bp.get("/<supplier_id>")
@roles_required(*_STAFF)
@permission_required(PERM_SUPPLIERS_READ)
def get_supplier(supplier_id):
    return supplier_controller.get_supplier(supplier_id)


@suppliers_bp.patch("/<supplier_id>")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_SUPPLIERS_WRITE)
def update_supplier(supplier_id):
    return supplier_controller.update_supplier(supplier_id)


@suppliers_bp.delete("/<supplier_id>")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_SUPPLIERS_WRITE)
def deactivate_supplier(supplier_id):
    return supplier_controller.deactivate_supplier(supplier_id)


@suppliers_bp.patch("/<supplier_id>/status")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_SUPPLIERS_WRITE)
def set_supplier_status(supplier_id):
    return supplier_controller.set_supplier_status(supplier_id)
