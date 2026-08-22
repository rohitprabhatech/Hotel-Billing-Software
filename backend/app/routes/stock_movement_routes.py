"""Stock movement ledger routes (owner + manager)."""

from flask import Blueprint

from app.constants.permissions import PERM_STOCK_MOVEMENTS
from app.controllers import stock_movement_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_MANAGER, ROLE_OWNER
from app.utils.permission_access import permission_required

stock_movements_bp = Blueprint("stock_movements", __name__, url_prefix="/stock-movements")


@stock_movements_bp.get("")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_STOCK_MOVEMENTS)
def list_movements():
    return stock_movement_controller.list_movements()
