"""Kitchen Order Ticket routes (BIZ-14)."""

from flask import Blueprint

from app.constants.permissions import PERM_KOT_READ, PERM_KOT_STATUS, PERM_KOT_WRITE
from app.controllers import kot_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

kots_bp = Blueprint("kots", __name__, url_prefix="/kots")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_OPS = (ROLE_OWNER, ROLE_MANAGER)


@kots_bp.get("")
@roles_required(*_STAFF)
@module_required("kitchen")
@permission_required(PERM_KOT_READ)
def list_kots():
    return kot_controller.list_kots()


@kots_bp.get("/kitchen/queue")
@roles_required(*_STAFF)
@module_required("kitchen")
@permission_required(PERM_KOT_READ)
def get_kitchen_queue():
    return kot_controller.get_kitchen_queue()


@kots_bp.get("/<kot_id>")
@roles_required(*_STAFF)
@module_required("kot")
@permission_required(PERM_KOT_READ)
def get_kot(kot_id):
    return kot_controller.get_kot(kot_id)


@kots_bp.patch("/<kot_id>/status")
@roles_required(*_STAFF)
@module_required("kitchen")
@permission_required(PERM_KOT_STATUS)
def update_kot_status(kot_id):
    return kot_controller.update_kot_status(kot_id)


@kots_bp.patch("/<kot_id>")
@roles_required(*_OPS)
@module_required("kitchen")
@permission_required(PERM_KOT_WRITE)
def update_kot(kot_id):
    return kot_controller.update_kot(kot_id)


@kots_bp.delete("/<kot_id>")
@roles_required(*_OPS)
@module_required("kitchen")
@permission_required(PERM_KOT_WRITE)
def delete_kot(kot_id):
    return kot_controller.delete_kot(kot_id)
