"""Bill routes."""

from flask import Blueprint

from app.controllers import bill_controller
from app.extensions import limiter
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER

bills_bp = Blueprint("bills", __name__, url_prefix="/bills")


@bills_bp.post("")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def create_bill():
    return bill_controller.create_bill()


@bills_bp.get("")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def list_bills():
    return bill_controller.list_bills()


@bills_bp.get("/today-summary")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def today_summary():
    return bill_controller.today_summary()


@bills_bp.get("/<bill_id>")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def get_bill(bill_id):
    return bill_controller.get_bill(bill_id)


@bills_bp.post("/<bill_id>/cancel")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def cancel_bill(bill_id):
    return bill_controller.cancel_bill(bill_id)


@bills_bp.post("/<bill_id>/print")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def print_bill(bill_id):
    return bill_controller.print_bill(bill_id)


@bills_bp.get("/<bill_id>/pdf")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
def download_bill_pdf(bill_id):
    return bill_controller.download_bill_pdf(bill_id)


@bills_bp.post("/<bill_id>/send-whatsapp")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
@limiter.limit("20 per minute")
def send_bill_whatsapp(bill_id):
    from app.controllers import whatsapp_controller

    return whatsapp_controller.send_bill_whatsapp(bill_id)


@bills_bp.post("/<bill_id>/send-email")
@roles_required(ROLE_OWNER, ROLE_BILLING_USER)
@limiter.limit("20 per minute")
def send_bill_email(bill_id):
    return bill_controller.send_bill_email(bill_id)