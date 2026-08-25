"""Sales return and exchange routes (BIZ-27)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import sales_return_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

returns_bp = Blueprint("sales_returns", __name__, url_prefix="/returns")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@returns_bp.get("/lookup")
@roles_required(*_STAFF)
@module_required("returns_exchange")
@permission_required(PERM_BILLING)
def lookup_bill():
    return sales_return_controller.lookup_bill()


@returns_bp.get("")
@roles_required(*_STAFF)
@module_required("returns_exchange")
@permission_required(PERM_BILLING)
def list_returns():
    return sales_return_controller.list_returns()


@returns_bp.post("")
@roles_required(*_WRITE)
@module_required("returns_exchange")
@permission_required(PERM_BILLING)
def create_return():
    return sales_return_controller.create_return()


@returns_bp.get("/<return_id>")
@roles_required(*_STAFF)
@module_required("returns_exchange")
@permission_required(PERM_BILLING)
def get_return(return_id):
    return sales_return_controller.get_return(return_id)
