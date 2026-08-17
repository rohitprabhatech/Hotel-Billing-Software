"""Owner stock movement ledger routes."""

from flask import Blueprint

from app.controllers import stock_movement_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_OWNER

stock_movements_bp = Blueprint("stock_movements", __name__, url_prefix="/stock-movements")


@stock_movements_bp.get("")
@roles_required(ROLE_OWNER)
def list_movements():
    return stock_movement_controller.list_movements()
