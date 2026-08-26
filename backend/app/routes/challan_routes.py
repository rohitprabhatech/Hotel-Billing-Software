"""Delivery challan routes (BIZ-36)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import challan_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

challans_bp = Blueprint("challans", __name__, url_prefix="/challans")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@challans_bp.get("")
@roles_required(*_READ)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def list_challans():
    return challan_controller.list_challans()


@challans_bp.post("")
@roles_required(*_WRITE)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def create_challan():
    return challan_controller.create_challan()


@challans_bp.get("/<challan_id>")
@roles_required(*_READ)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def get_challan(challan_id):
    return challan_controller.get_challan(challan_id)


@challans_bp.patch("/<challan_id>/status")
@roles_required(*_WRITE)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def update_challan_status(challan_id):
    return challan_controller.update_challan_status(challan_id)


@challans_bp.post("/<challan_id>/convert")
@roles_required(*_WRITE)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def convert_challan(challan_id):
    return challan_controller.convert_challan(challan_id)


@challans_bp.get("/<challan_id>/pdf")
@roles_required(*_READ)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def download_challan_pdf(challan_id):
    return challan_controller.download_challan_pdf(challan_id)
