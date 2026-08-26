"""Book store catalog routes (BIZ-45) — thin aliases over items metadata."""

from flask import Blueprint, request

from app.constants.permissions import PERM_ITEMS_READ
from app.controllers import item_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.services.item_service import ItemService
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required
from app.utils.responses import success_response

books_bp = Blueprint("books", __name__, url_prefix="/books")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@books_bp.get("/catalog")
@roles_required(*_STAFF)
@module_required("book_metadata")
@permission_required(PERM_ITEMS_READ)
def catalog():
    """Search book catalog via shared items list (q matches ISBN/author/publisher)."""
    return item_controller.list_items()


@books_bp.get("/by-isbn/<isbn>")
@roles_required(*_STAFF)
@module_required("book_metadata")
@permission_required(PERM_ITEMS_READ)
def by_isbn(isbn: str):
    active_only = request.args.get("active_only", "true").lower() not in {"0", "false", "no"}
    data = ItemService.get_item_by_isbn(isbn, active_only=active_only)
    return success_response(data=data)
