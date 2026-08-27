"""Dining table routes (BIZ-12)."""

from flask import Blueprint

from app.constants.permissions import PERM_TABLES_READ, PERM_TABLES_STATUS, PERM_TABLES_WRITE
from app.controllers import dining_table_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

tables_bp = Blueprint("tables", __name__, url_prefix="/tables")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@tables_bp.get("")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_READ)
def list_tables():
    return dining_table_controller.list_tables()


@tables_bp.post("")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_WRITE)
def create_table():
    return dining_table_controller.create_table()


@tables_bp.post("/merge")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_STATUS)
def merge_tables():
    return dining_table_controller.merge_tables()


@tables_bp.post("/unmerge")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_STATUS)
def unmerge_tables():
    return dining_table_controller.unmerge_tables()


@tables_bp.get("/<table_id>")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_READ)
def get_table(table_id):
    return dining_table_controller.get_table(table_id)


@tables_bp.get("/<table_id>/bills")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_READ)
def list_table_bills(table_id):
    return dining_table_controller.list_table_bills(table_id)


@tables_bp.patch("/<table_id>")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_WRITE)
def update_table(table_id):
    return dining_table_controller.update_table(table_id)


@tables_bp.delete("/<table_id>")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_WRITE)
def deactivate_table(table_id):
    return dining_table_controller.deactivate_table(table_id)


@tables_bp.post("/<table_id>/status")
@roles_required(*_STAFF)
@module_required("table_management")
@permission_required(PERM_TABLES_STATUS)
def set_table_status(table_id):
    return dining_table_controller.set_table_status(table_id)
