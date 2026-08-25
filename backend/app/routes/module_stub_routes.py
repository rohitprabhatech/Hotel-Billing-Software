"""Module-gated item variant catalog (BIZ-25)."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ
from app.controllers import item_variant_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

variants_bp = Blueprint("item_variants", __name__, url_prefix="/item-variants")


@variants_bp.get("")
@roles_required(ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
@module_required("variants")
@permission_required(PERM_ITEMS_READ)
def list_variants():
    return item_variant_controller.list_tenant_variants()
