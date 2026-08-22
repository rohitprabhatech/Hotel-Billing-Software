"""Customer master routes (BIZ-04)."""

from flask import Blueprint

from app.constants.permissions import PERM_CUSTOMERS_READ, PERM_CUSTOMERS_WRITE
from app.controllers import customer_controller, party_ledger_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.permission_access import permission_required

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@customers_bp.get("")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_READ)
def list_customers():
    return customer_controller.list_customers()


@customers_bp.post("")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_WRITE)
def create_customer():
    return customer_controller.create_customer()


@customers_bp.get("/<customer_id>")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_READ)
def get_customer(customer_id):
    return customer_controller.get_customer(customer_id)


@customers_bp.patch("/<customer_id>")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_WRITE)
def update_customer(customer_id):
    return customer_controller.update_customer(customer_id)


@customers_bp.delete("/<customer_id>")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_WRITE)
def deactivate_customer(customer_id):
    return customer_controller.deactivate_customer(customer_id)


@customers_bp.patch("/<customer_id>/status")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_WRITE)
def set_customer_status(customer_id):
    return customer_controller.set_customer_status(customer_id)


@customers_bp.get("/outstanding")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_READ)
def list_outstanding():
    return party_ledger_controller.list_outstanding()


@customers_bp.get("/<customer_id>/ledger")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_READ)
def list_customer_ledger(customer_id):
    return party_ledger_controller.list_customer_ledger(customer_id)


@customers_bp.post("/<customer_id>/payments")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_WRITE)
def record_customer_payment(customer_id):
    return party_ledger_controller.record_customer_payment(customer_id)


@customers_bp.get("/<customer_id>/bills")
@roles_required(*_STAFF)
@permission_required(PERM_CUSTOMERS_READ)
def list_customer_bills(customer_id):
    return customer_controller.list_customer_bills(customer_id)
