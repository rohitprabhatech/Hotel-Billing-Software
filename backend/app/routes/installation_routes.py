"""Installation job routes (BIZ-33)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import installation_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

installations_bp = Blueprint("installations", __name__, url_prefix="/installations")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@installations_bp.get("")
@roles_required(*_READ)
@module_required("installation")
@permission_required(PERM_BILLING)
def list_installations():
    return installation_controller.list_installations()


@installations_bp.post("")
@roles_required(*_WRITE)
@module_required("installation")
@permission_required(PERM_BILLING)
def create_installation():
    return installation_controller.create_installation()


@installations_bp.get("/<installation_id>")
@roles_required(*_READ)
@module_required("installation")
@permission_required(PERM_BILLING)
def get_installation(installation_id):
    return installation_controller.get_installation(installation_id)


@installations_bp.patch("/<installation_id>/status")
@roles_required(*_WRITE)
@module_required("installation")
@permission_required(PERM_BILLING)
def update_installation_status(installation_id):
    return installation_controller.update_installation_status(installation_id)
