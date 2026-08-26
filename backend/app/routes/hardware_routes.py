"""Hardware measurement POS and quote routes (BIZ-35)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING, PERM_ITEMS_READ
from app.controllers import hardware_pos_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

hardware_bp = Blueprint("hardware", __name__, url_prefix="/hardware")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@hardware_bp.get("/units")
@roles_required(*_STAFF)
@module_required("uom_measurement")
@permission_required(PERM_ITEMS_READ)
def units_catalog():
    return hardware_pos_controller.units_catalog()


@hardware_bp.get("/pos-catalog")
@roles_required(*_STAFF)
@module_required("uom_measurement")
@permission_required(PERM_ITEMS_READ)
def pos_catalog():
    return hardware_pos_controller.pos_catalog()


@hardware_bp.post("/quote")
@roles_required(*_STAFF)
@module_required("uom_measurement")
@permission_required(PERM_BILLING)
def quote():
    return hardware_pos_controller.quote()


@hardware_bp.post("/convert")
@roles_required(*_STAFF)
@module_required("uom_measurement")
@permission_required(PERM_ITEMS_READ)
def convert():
    return hardware_pos_controller.convert()
