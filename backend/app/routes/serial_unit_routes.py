"""Serial / IMEI unit routes (BIZ-29). Shared by mobile and electronics."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK
from app.controllers import serial_unit_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

serial_units_bp = Blueprint("serial_units", __name__, url_prefix="/serial-units")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@serial_units_bp.get("")
@roles_required(*_STAFF)
@module_required("serial_imei")
@permission_required(PERM_ITEMS_READ)
def list_units():
    return serial_unit_controller.list_units()


@serial_units_bp.get("/by-serial/<serial>")
@roles_required(*_STAFF)
@module_required("serial_imei")
@permission_required(PERM_ITEMS_READ)
def get_by_serial(serial):
    return serial_unit_controller.get_by_serial(serial)


@serial_units_bp.post("")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@module_required("serial_imei")
@permission_required(PERM_ITEMS_STOCK)
def receive():
    return serial_unit_controller.receive()
