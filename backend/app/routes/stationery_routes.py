"""Stationery fast POS routes (BIZ-44) — thin reuse of barcode POS catalog."""

from flask import Blueprint, request

from app.constants.permissions import PERM_ITEMS_READ
from app.controllers import grocery_pos_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.services.item_service import ItemService
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required
from app.utils.responses import success_response

stationery_bp = Blueprint("stationery", __name__, url_prefix="/stationery")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@stationery_bp.get("/pos-catalog")
@roles_required(*_STAFF)
@module_required("barcode_pos")
@permission_required(PERM_ITEMS_READ)
def pos_catalog():
    """Same contract as grocery pos-catalog (search via ?q=)."""
    return grocery_pos_controller.pos_catalog()


@stationery_bp.get("/products/search")
@roles_required(*_STAFF)
@module_required("barcode_pos")
@permission_required(PERM_ITEMS_READ)
def products_search():
    """Search-first alias — returns catalog items matching q."""
    return grocery_pos_controller.pos_catalog()


@stationery_bp.get("/products/by-barcode/<barcode>")
@roles_required(*_STAFF)
@module_required("barcode_pos")
@permission_required(PERM_ITEMS_READ)
def product_by_barcode(barcode: str):
    active_only = request.args.get("active_only", "true").lower() != "false"
    data = ItemService.get_item_by_barcode(barcode, active_only=active_only)
    return success_response(data=data)
