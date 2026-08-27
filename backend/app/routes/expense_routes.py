"""Expense routes (BIZ-07)."""

from flask import Blueprint

from app.constants.permissions import PERM_EXPENSES_READ, PERM_EXPENSES_WRITE
from app.controllers import expense_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.permission_access import permission_required

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")

# BILLING_USER allowed at role layer; hotel-only extra perms enforce industry scope.
_OPS = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@expenses_bp.get("")
@roles_required(*_OPS)
@permission_required(PERM_EXPENSES_READ)
def list_expenses():
    return expense_controller.list_expenses()


@expenses_bp.get("/summary")
@roles_required(*_OPS)
@permission_required(PERM_EXPENSES_READ)
def expense_summary():
    return expense_controller.expense_summary()


@expenses_bp.post("")
@roles_required(*_OPS)
@permission_required(PERM_EXPENSES_WRITE)
def create_expense():
    return expense_controller.create_expense()


@expenses_bp.get("/<expense_id>")
@roles_required(*_OPS)
@permission_required(PERM_EXPENSES_READ)
def get_expense(expense_id):
    return expense_controller.get_expense(expense_id)


@expenses_bp.patch("/<expense_id>")
@roles_required(*_OPS)
@permission_required(PERM_EXPENSES_WRITE)
def update_expense(expense_id):
    return expense_controller.update_expense(expense_id)


@expenses_bp.delete("/<expense_id>")
@roles_required(*_OPS)
@permission_required(PERM_EXPENSES_WRITE)
def delete_expense(expense_id):
    return expense_controller.delete_expense(expense_id)
