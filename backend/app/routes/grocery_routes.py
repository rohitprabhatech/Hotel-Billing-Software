"""Grocery fast POS routes (BIZ-20) and credit/sales aliases (BIZ-23)."""

from flask import Blueprint

from app.constants.permissions import (
    PERM_CUSTOMERS_READ,
    PERM_CUSTOMERS_WRITE,
    PERM_ITEMS_READ,
    PERM_REPORTS,
)
from app.controllers import grocery_credit_controller, grocery_pos_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

grocery_bp = Blueprint("grocery", __name__, url_prefix="/grocery")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@grocery_bp.get("/pos-catalog")
@roles_required(*_STAFF)
@module_required("barcode_pos")
@permission_required(PERM_ITEMS_READ)
def pos_catalog():
    return grocery_pos_controller.pos_catalog()


@grocery_bp.get("/expiry")
@roles_required(*_STAFF)
@module_required("batch_expiry")
@permission_required(PERM_ITEMS_READ)
def grocery_expiry():
    """Alias for GET /batches/expiry (grocery docs)."""
    from app.controllers import batch_controller

    return batch_controller.expiry_report()


@grocery_bp.get("/outstanding")
@roles_required(*_STAFF)
@module_required("customer_credit")
@permission_required(PERM_CUSTOMERS_READ)
def grocery_outstanding():
    return grocery_credit_controller.list_outstanding()


@grocery_bp.get("/credit/<customer_id>")
@roles_required(*_STAFF)
@module_required("customer_credit")
@permission_required(PERM_CUSTOMERS_READ)
def grocery_credit(customer_id):
    return grocery_credit_controller.customer_credit(customer_id)


@grocery_bp.post("/credit/<customer_id>/pay")
@roles_required(*_STAFF)
@module_required("customer_credit")
@permission_required(PERM_CUSTOMERS_WRITE)
def grocery_credit_pay(customer_id):
    return grocery_credit_controller.record_payment(customer_id)


@grocery_bp.get("/sales")
@roles_required(ROLE_OWNER, ROLE_MANAGER)
@module_required("barcode_pos")
@permission_required(PERM_REPORTS)
def grocery_sales():
    return grocery_credit_controller.sales_report()
