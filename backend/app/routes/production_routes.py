"""Production routes (BIZ-40)."""

from flask import Blueprint

from app.constants.permissions import PERM_PRODUCTION_READ, PERM_PRODUCTION_WRITE
from app.controllers import production_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

productions_bp = Blueprint("productions", __name__, url_prefix="/productions")

_OPS = (ROLE_OWNER, ROLE_MANAGER)


@productions_bp.get("")
@roles_required(*_OPS)
@module_required("production")
@permission_required(PERM_PRODUCTION_READ)
def list_productions():
    return production_controller.list_productions()


@productions_bp.post("")
@roles_required(*_OPS)
@module_required("production")
@permission_required(PERM_PRODUCTION_WRITE)
def create_production():
    return production_controller.create_production()


@productions_bp.get("/<run_id>")
@roles_required(*_OPS)
@module_required("production")
@permission_required(PERM_PRODUCTION_READ)
def get_production(run_id):
    return production_controller.get_production(run_id)
