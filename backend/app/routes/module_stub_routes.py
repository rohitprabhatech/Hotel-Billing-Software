"""Module-gated industry stub routes (BIZ-02 framework).

Full industry CRUD arrives in later sprints. These endpoints prove the gate:
enabled → 200 empty payload; disabled → 403.
"""

from flask import Blueprint

from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.responses import success_response

tables_bp = Blueprint("tables", __name__, url_prefix="/tables")
variants_bp = Blueprint("item_variants", __name__, url_prefix="/item-variants")


@tables_bp.get("")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
@module_required("table_management")
def list_tables():
    return success_response(
        data={
            "items": [],
            "module": "table_management",
            "message": "Table management module is enabled. Full CRUD arrives in a later sprint.",
        }
    )


@variants_bp.get("")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
@module_required("variants")
def list_variants():
    return success_response(
        data={
            "items": [],
            "module": "variants",
            "message": "Variants module is enabled. Full CRUD arrives in a later sprint.",
        }
    )
