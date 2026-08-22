"""Bill routes."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import bill_controller
from app.extensions import limiter
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.permission_access import permission_required

bills_bp = Blueprint("bills", __name__, url_prefix="/bills")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@bills_bp.post("")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def create_bill():
    return bill_controller.create_bill()


@bills_bp.post("/split")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def split_order_bills():
    return bill_controller.split_order_bills()


@bills_bp.get("")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def list_bills():
    return bill_controller.list_bills()


@bills_bp.get("/today-summary")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def today_summary():
    return bill_controller.today_summary()


@bills_bp.get("/<bill_id>")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def get_bill(bill_id):
    return bill_controller.get_bill(bill_id)


@bills_bp.post("/<bill_id>/cancel")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def cancel_bill(bill_id):
    return bill_controller.cancel_bill(bill_id)


@bills_bp.post("/<bill_id>/print")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def print_bill(bill_id):
    return bill_controller.print_bill(bill_id)


@bills_bp.get("/<bill_id>/pdf")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
def download_bill_pdf(bill_id):
    return bill_controller.download_bill_pdf(bill_id)


@bills_bp.post("/<bill_id>/send-whatsapp")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
@limiter.limit("20 per minute")
def send_bill_whatsapp(bill_id):
    from app.controllers import whatsapp_controller

    return whatsapp_controller.send_bill_whatsapp(bill_id)


@bills_bp.post("/<bill_id>/send-email")
@roles_required(*_STAFF)
@permission_required(PERM_BILLING)
@limiter.limit("20 per minute")
def send_bill_email(bill_id):
    return bill_controller.send_bill_email(bill_id)