"""Coupon routes (Sprint 5 — cafe pack)."""

from flask import Blueprint

from app.constants.permissions import PERM_ADDONS_READ, PERM_ADDONS_WRITE, PERM_BILLING
from app.controllers import coupon_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

coupons_bp = Blueprint("coupons", __name__, url_prefix="/coupons")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_OPS = (ROLE_OWNER, ROLE_MANAGER)


@coupons_bp.get("")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_READ)
def list_coupons():
    return coupon_controller.list_coupons()


@coupons_bp.post("")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_WRITE)
def create_coupon():
    return coupon_controller.create_coupon()


@coupons_bp.post("/preview")
@roles_required(*_STAFF)
@module_required("addons_combos")
@permission_required(PERM_BILLING)
def preview_coupon():
    return coupon_controller.preview_coupon()


@coupons_bp.get("/<coupon_id>")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_READ)
def get_coupon(coupon_id):
    return coupon_controller.get_coupon(coupon_id)


@coupons_bp.put("/<coupon_id>")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_WRITE)
def update_coupon(coupon_id):
    return coupon_controller.update_coupon(coupon_id)


@coupons_bp.delete("/<coupon_id>")
@roles_required(*_OPS)
@module_required("addons_combos")
@permission_required(PERM_ADDONS_WRITE)
def deactivate_coupon(coupon_id):
    return coupon_controller.deactivate_coupon(coupon_id)
