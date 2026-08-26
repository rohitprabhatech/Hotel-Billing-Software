"""Warehouse and stock-transfer routes (BIZ-38)."""

from flask import Blueprint

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK
from app.controllers import warehouse_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

warehouses_bp = Blueprint("warehouses", __name__, url_prefix="/warehouses")
stock_transfers_bp = Blueprint("stock_transfers", __name__, url_prefix="/stock-transfers")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@warehouses_bp.get("")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def list_warehouses():
    return warehouse_controller.list_warehouses()


@warehouses_bp.post("")
@roles_required(*_WRITE)
@module_required("warehouse")
@permission_required(PERM_ITEMS_STOCK)
def create_warehouse():
    return warehouse_controller.create_warehouse()


@warehouses_bp.patch("/<warehouse_id>")
@roles_required(*_WRITE)
@module_required("warehouse")
@permission_required(PERM_ITEMS_STOCK)
def update_warehouse(warehouse_id):
    return warehouse_controller.update_warehouse(warehouse_id)


@warehouses_bp.get("/stocks")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def list_stocks():
    return warehouse_controller.list_stocks()


@stock_transfers_bp.get("")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def list_transfers():
    return warehouse_controller.list_transfers()


@stock_transfers_bp.post("")
@roles_required(*_WRITE)
@module_required("warehouse")
@permission_required(PERM_ITEMS_STOCK)
def create_transfer():
    return warehouse_controller.create_transfer()


@stock_transfers_bp.get("/<transfer_id>")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def get_transfer(transfer_id):
    return warehouse_controller.get_transfer(transfer_id)
