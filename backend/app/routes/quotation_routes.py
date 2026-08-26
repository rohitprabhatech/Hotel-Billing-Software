"""Quotation routes (BIZ-36)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import quotation_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

quotations_bp = Blueprint("quotations", __name__, url_prefix="/quotations")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@quotations_bp.get("")
@roles_required(*_READ)
@module_required("quotation")
@permission_required(PERM_BILLING)
def list_quotations():
    return quotation_controller.list_quotations()


@quotations_bp.post("")
@roles_required(*_WRITE)
@module_required("quotation")
@permission_required(PERM_BILLING)
def create_quotation():
    return quotation_controller.create_quotation()


@quotations_bp.get("/<quotation_id>")
@roles_required(*_READ)
@module_required("quotation")
@permission_required(PERM_BILLING)
def get_quotation(quotation_id):
    return quotation_controller.get_quotation(quotation_id)


@quotations_bp.patch("/<quotation_id>/status")
@roles_required(*_WRITE)
@module_required("quotation")
@permission_required(PERM_BILLING)
def update_quotation_status(quotation_id):
    return quotation_controller.update_quotation_status(quotation_id)


@quotations_bp.post("/<quotation_id>/convert")
@roles_required(*_WRITE)
@module_required("quotation")
@permission_required(PERM_BILLING)
def convert_quotation(quotation_id):
    return quotation_controller.convert_quotation(quotation_id)
