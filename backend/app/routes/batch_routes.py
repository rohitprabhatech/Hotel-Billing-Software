"""Batch / expiry routes (BIZ-22)."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK
from app.controllers import batch_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

batches_bp = Blueprint("batches", __name__, url_prefix="/batches")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@batches_bp.get("")
@roles_required(*_STAFF)
@module_required("batch_expiry")
@permission_required(PERM_ITEMS_READ)
def list_batches():
    return batch_controller.list_batches()


@batches_bp.get("/expiry")
@roles_required(*_STAFF)
@module_required("batch_expiry")
@permission_required(PERM_ITEMS_READ)
def expiry_report():
    return batch_controller.expiry_report()


@batches_bp.post("")
@roles_required(ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
@module_required("batch_expiry")
@permission_required(PERM_ITEMS_STOCK)
def create_batch():
    return batch_controller.create_batch()


@batches_bp.post("/<batch_id>/adjust")
@roles_required(ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
@module_required("batch_expiry")
@permission_required(PERM_ITEMS_STOCK)
def adjust_batch(batch_id):
    return batch_controller.adjust_batch(batch_id)
