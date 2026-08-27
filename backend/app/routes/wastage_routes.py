"""Wastage routes (BIZ-18)."""

from flask import Blueprint

from app.constants.permissions import PERM_WASTAGE_READ, PERM_WASTAGE_WRITE
from app.controllers import wastage_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

wastage_bp = Blueprint("wastage", __name__, url_prefix="/wastage")

# BILLING_USER allowed at role layer; hotel-only extra perms enforce industry scope.
_OPS = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@wastage_bp.get("")
@roles_required(*_OPS)
@module_required("wastage")
@permission_required(PERM_WASTAGE_READ)
def list_wastage():
    return wastage_controller.list_wastage()


@wastage_bp.post("")
@roles_required(*_OPS)
@module_required("wastage")
@permission_required(PERM_WASTAGE_WRITE)
def create_wastage():
    return wastage_controller.create_wastage()


@wastage_bp.get("/<wastage_id>")
@roles_required(*_OPS)
@module_required("wastage")
@permission_required(PERM_WASTAGE_READ)
def get_wastage(wastage_id):
    return wastage_controller.get_wastage(wastage_id)
