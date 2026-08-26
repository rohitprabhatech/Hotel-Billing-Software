"""Repair / service ticket routes (BIZ-31)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import repair_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

repairs_bp = Blueprint("repairs", __name__, url_prefix="/repairs")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@repairs_bp.get("")
@roles_required(*_READ)
@module_required("repair_service")
@permission_required(PERM_BILLING)
def list_repairs():
    return repair_controller.list_repairs()


@repairs_bp.post("")
@roles_required(*_WRITE)
@module_required("repair_service")
@permission_required(PERM_BILLING)
def create_repair():
    return repair_controller.create_repair()


@repairs_bp.get("/<repair_id>")
@roles_required(*_READ)
@module_required("repair_service")
@permission_required(PERM_BILLING)
def get_repair(repair_id):
    return repair_controller.get_repair(repair_id)


@repairs_bp.patch("/<repair_id>/status")
@roles_required(*_WRITE)
@module_required("repair_service")
@permission_required(PERM_BILLING)
def update_repair_status(repair_id):
    return repair_controller.update_repair_status(repair_id)
