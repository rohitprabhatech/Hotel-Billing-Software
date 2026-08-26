"""Wholesale convenience routes (BIZ-51…54) — price lists, SO, PO, warehouses, reports, challans."""

from flask import Blueprint

from app.constants.permissions import (
    PERM_BILLING,
    PERM_ITEMS_READ,
    PERM_ITEMS_STOCK,
    PERM_ITEMS_WRITE,
    PERM_PURCHASES_READ,
    PERM_PURCHASES_WRITE,
    PERM_REPORTS,
)
from app.controllers import (
    challan_controller,
    price_list_controller,
    purchase_order_controller,
    report_controller,
    sales_order_controller,
    warehouse_controller,
)
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

wholesale_bp = Blueprint("wholesale", __name__, url_prefix="/wholesale")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@wholesale_bp.get("/price-lists")
@roles_required(*_READ)
@module_required("price_lists")
@permission_required(PERM_ITEMS_READ)
def list_wholesale_price_lists():
    return price_list_controller.list_price_lists()


@wholesale_bp.post("/price-lists")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def create_wholesale_price_list():
    return price_list_controller.create_price_list()


@wholesale_bp.get("/price-lists/<price_list_id>")
@roles_required(*_READ)
@module_required("price_lists")
@permission_required(PERM_ITEMS_READ)
def get_wholesale_price_list(price_list_id):
    return price_list_controller.get_price_list(price_list_id)


@wholesale_bp.patch("/price-lists/<price_list_id>")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def update_wholesale_price_list(price_list_id):
    return price_list_controller.update_price_list(price_list_id)


@wholesale_bp.put("/price-lists/<price_list_id>/items")
@roles_required(*_WRITE)
@module_required("price_lists")
@permission_required(PERM_ITEMS_WRITE)
def replace_wholesale_price_list_items(price_list_id):
    return price_list_controller.replace_price_list_items(price_list_id)


@wholesale_bp.get("/sales-orders")
@roles_required(*_READ)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def list_wholesale_sales_orders():
    return sales_order_controller.list_sales_orders()


@wholesale_bp.post("/sales-orders")
@roles_required(*_WRITE)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def create_wholesale_sales_order():
    return sales_order_controller.create_sales_order()


@wholesale_bp.post("/sales-orders/<order_id>/convert")
@roles_required(*_WRITE)
@module_required("sales_orders")
@permission_required(PERM_BILLING)
def convert_wholesale_sales_order(order_id):
    return sales_order_controller.convert_sales_order(order_id)


@wholesale_bp.get("/purchase-orders")
@roles_required(*_READ)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_READ)
def list_wholesale_purchase_orders():
    return purchase_order_controller.list_purchase_orders()


@wholesale_bp.post("/purchase-orders")
@roles_required(*_WRITE)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_WRITE)
def create_wholesale_purchase_order():
    return purchase_order_controller.create_purchase_order()


@wholesale_bp.post("/purchase-orders/<order_id>/convert")
@roles_required(*_WRITE)
@module_required("purchase_orders")
@permission_required(PERM_PURCHASES_WRITE)
def convert_wholesale_purchase_order(order_id):
    return purchase_order_controller.convert_purchase_order(order_id)


@wholesale_bp.get("/warehouses")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def list_wholesale_warehouses():
    return warehouse_controller.list_warehouses()


@wholesale_bp.post("/warehouses")
@roles_required(*_WRITE)
@module_required("warehouse")
@permission_required(PERM_ITEMS_STOCK)
def create_wholesale_warehouse():
    return warehouse_controller.create_warehouse()


@wholesale_bp.patch("/warehouses/<warehouse_id>")
@roles_required(*_WRITE)
@module_required("warehouse")
@permission_required(PERM_ITEMS_STOCK)
def update_wholesale_warehouse(warehouse_id):
    return warehouse_controller.update_warehouse(warehouse_id)


@wholesale_bp.get("/warehouses/stocks")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def list_wholesale_stocks():
    return warehouse_controller.list_stocks()


@wholesale_bp.get("/stock-transfers")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def list_wholesale_transfers():
    return warehouse_controller.list_transfers()


@wholesale_bp.post("/stock-transfers")
@roles_required(*_WRITE)
@module_required("warehouse")
@permission_required(PERM_ITEMS_STOCK)
def create_wholesale_transfer():
    return warehouse_controller.create_transfer()


@wholesale_bp.get("/stock-transfers/<transfer_id>")
@roles_required(*_READ)
@module_required("warehouse")
@permission_required(PERM_ITEMS_READ)
def get_wholesale_transfer(transfer_id):
    return warehouse_controller.get_transfer(transfer_id)


@wholesale_bp.get("/reports/outstanding")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@permission_required(PERM_REPORTS)
def wholesale_outstanding_report():
    return report_controller.outstanding()


@wholesale_bp.get("/challans")
@roles_required(*_READ)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def list_wholesale_challans():
    return challan_controller.list_challans()


@wholesale_bp.post("/challans")
@roles_required(*_WRITE)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def create_wholesale_challan():
    return challan_controller.create_challan()


@wholesale_bp.get("/challans/<challan_id>")
@roles_required(*_READ)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def get_wholesale_challan(challan_id):
    return challan_controller.get_challan(challan_id)


@wholesale_bp.get("/challans/<challan_id>/pdf")
@roles_required(*_READ)
@module_required("delivery_challan")
@permission_required(PERM_BILLING)
def wholesale_challan_pdf(challan_id):
    return challan_controller.download_challan_pdf(challan_id)
