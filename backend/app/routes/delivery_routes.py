"""Delivery job routes (BIZ-49)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import delivery_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

deliveries_bp = Blueprint("deliveries", __name__, url_prefix="/deliveries")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@deliveries_bp.get("")
@roles_required(*_READ)
@module_required("delivery_tracking")
@permission_required(PERM_BILLING)
def list_deliveries():
    return delivery_controller.list_deliveries()


@deliveries_bp.post("")
@roles_required(*_WRITE)
@module_required("delivery_tracking")
@permission_required(PERM_BILLING)
def create_delivery():
    return delivery_controller.create_delivery()


@deliveries_bp.get("/<delivery_id>")
@roles_required(*_READ)
@module_required("delivery_tracking")
@permission_required(PERM_BILLING)
def get_delivery(delivery_id):
    return delivery_controller.get_delivery(delivery_id)


@deliveries_bp.patch("/<delivery_id>/status")
@roles_required(*_WRITE)
@module_required("delivery_tracking")
@permission_required(PERM_BILLING)
def update_delivery_status(delivery_id):
    return delivery_controller.update_delivery_status(delivery_id)
