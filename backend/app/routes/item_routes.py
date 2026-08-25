"""Item routes — tenant staff with permission matrix (BIZ-03)."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK, PERM_ITEMS_WRITE
from app.controllers import (
    item_accessory_controller,
    item_controller,
    item_image_controller,
    item_price_tier_controller,
    item_variant_controller,
)
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

items_bp = Blueprint("items", __name__, url_prefix="/items")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@items_bp.get("")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_READ)
def list_items():
    return item_controller.list_items()


@items_bp.post("")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def create_item():
    return item_controller.create_item()


@items_bp.get("/by-barcode/<barcode>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_READ)
def get_item_by_barcode(barcode):
    return item_controller.get_item_by_barcode(barcode)


@items_bp.get("/<item_id>/price-tiers")
@roles_required(*_STAFF)
@module_required("bulk_pricing")
@permission_required(PERM_ITEMS_READ)
def list_price_tiers(item_id):
    return item_price_tier_controller.list_price_tiers(item_id)


@items_bp.post("/<item_id>/price-tiers")
@roles_required(*_STAFF)
@module_required("bulk_pricing")
@permission_required(PERM_ITEMS_WRITE)
def create_price_tier(item_id):
    return item_price_tier_controller.create_price_tier(item_id)


@items_bp.put("/<item_id>/price-tiers")
@roles_required(*_STAFF)
@module_required("bulk_pricing")
@permission_required(PERM_ITEMS_WRITE)
def replace_price_tiers(item_id):
    return item_price_tier_controller.replace_price_tiers(item_id)


@items_bp.delete("/<item_id>/price-tiers/<tier_id>")
@roles_required(*_STAFF)
@module_required("bulk_pricing")
@permission_required(PERM_ITEMS_WRITE)
def delete_price_tier(item_id, tier_id):
    return item_price_tier_controller.delete_price_tier(item_id, tier_id)


@items_bp.get("/<item_id>/variants")
@roles_required(*_STAFF)
@module_required("variants")
@permission_required(PERM_ITEMS_READ)
def list_item_variants(item_id):
    return item_variant_controller.list_item_variants(item_id)


@items_bp.post("/<item_id>/variants")
@roles_required(*_STAFF)
@module_required("variants")
@permission_required(PERM_ITEMS_WRITE)
def create_item_variant(item_id):
    return item_variant_controller.create_item_variant(item_id)


@items_bp.put("/<item_id>/variants")
@roles_required(*_STAFF)
@module_required("variants")
@permission_required(PERM_ITEMS_WRITE)
def replace_item_variants(item_id):
    return item_variant_controller.replace_item_variants(item_id)


@items_bp.patch("/<item_id>/variants/<variant_id>")
@roles_required(*_STAFF)
@module_required("variants")
@permission_required(PERM_ITEMS_WRITE)
def update_item_variant(item_id, variant_id):
    return item_variant_controller.update_item_variant(item_id, variant_id)


@items_bp.delete("/<item_id>/variants/<variant_id>")
@roles_required(*_STAFF)
@module_required("variants")
@permission_required(PERM_ITEMS_WRITE)
def delete_item_variant(item_id, variant_id):
    return item_variant_controller.delete_item_variant(item_id, variant_id)


@items_bp.get("/<item_id>/images")
@roles_required(*_STAFF)
@module_required("product_images")
@permission_required(PERM_ITEMS_READ)
def list_item_images(item_id):
    return item_image_controller.list_item_images(item_id)


@items_bp.post("/<item_id>/images")
@roles_required(*_STAFF)
@module_required("product_images")
@permission_required(PERM_ITEMS_WRITE)
def create_item_image(item_id):
    return item_image_controller.create_item_image(item_id)


@items_bp.post("/<item_id>/images/upload")
@roles_required(*_STAFF)
@module_required("product_images")
@permission_required(PERM_ITEMS_WRITE)
def upload_item_image(item_id):
    return item_image_controller.upload_item_image(item_id)


@items_bp.delete("/<item_id>/images/<image_id>")
@roles_required(*_STAFF)
@module_required("product_images")
@permission_required(PERM_ITEMS_WRITE)
def delete_item_image(item_id, image_id):
    return item_image_controller.delete_item_image(item_id, image_id)


@items_bp.get("/<item_id>/accessories")
@roles_required(*_STAFF)
@module_required("warranty")
@permission_required(PERM_ITEMS_READ)
def list_item_accessories(item_id):
    return item_accessory_controller.list_item_accessories(item_id)


@items_bp.put("/<item_id>/accessories")
@roles_required(*_STAFF)
@module_required("warranty")
@permission_required(PERM_ITEMS_WRITE)
def replace_item_accessories(item_id):
    return item_accessory_controller.replace_item_accessories(item_id)


@items_bp.get("/<item_id>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_READ)
def get_item(item_id):
    return item_controller.get_item(item_id)


@items_bp.put("/<item_id>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def update_item(item_id):
    return item_controller.update_item(item_id)


@items_bp.patch("/<item_id>/status")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def set_item_status(item_id):
    return item_controller.set_item_status(item_id)


@items_bp.post("/<item_id>/adjust-stock")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_STOCK)
def adjust_stock(item_id):
    return item_controller.adjust_stock(item_id)


@items_bp.post("/<item_id>/receive-stock")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_STOCK)
def receive_stock(item_id):
    return item_controller.receive_stock(item_id)


@items_bp.delete("/<item_id>")
@roles_required(*_STAFF)
@permission_required(PERM_ITEMS_WRITE)
def delete_item(item_id):
    """Hard delete is intentionally unsupported — returns 405 via controller."""
    return item_controller.delete_item(item_id)
