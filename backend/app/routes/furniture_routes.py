"""Furniture convenience routes (BIZ-48 / BIZ-49) — custom orders, deliveries, installations."""

from flask import Blueprint, request

from app.constants.permissions import PERM_BILLING
from app.controllers import (
    custom_order_controller,
    delivery_controller,
    installation_controller,
    quotation_controller,
)
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.schemas.custom_order_schemas import create_custom_order_schema
from app.services.custom_order_service import CustomOrderService
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required
from app.utils.responses import success_response

furniture_bp = Blueprint("furniture", __name__, url_prefix="/furniture")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER)


@furniture_bp.get("/custom-orders")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def list_furniture_orders():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    status = request.args.get("status")
    data, meta = CustomOrderService.list_orders(
        order_type="furniture",
        status=status,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


@furniture_bp.post("/custom-orders")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def create_furniture_order():
    payload = create_custom_order_schema.load(request.get_json() or {})
    data = CustomOrderService.create(
        order_type="furniture",
        customer_id=payload.get("customer_id"),
        customer_name=payload.get("customer_name"),
        customer_phone=payload.get("customer_phone"),
        title=payload["title"],
        size=payload.get("size"),
        flavor=payload.get("flavor"),
        quantity=payload.get("quantity") or 1,
        total_amount=payload["total_amount"],
        advance_amount=payload.get("advance_amount") or 0,
        payment_method=payload.get("payment_method") or "cash",
        delivery_at=payload.get("delivery_at"),
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)


@furniture_bp.post("/custom-orders/<order_id>/advance")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def furniture_order_advance(order_id):
    return custom_order_controller.record_advance(order_id)


@furniture_bp.get("/deliveries")
@roles_required(*_STAFF)
@module_required("delivery_tracking")
@permission_required(PERM_BILLING)
def list_furniture_deliveries():
    return delivery_controller.list_deliveries()


@furniture_bp.post("/deliveries")
@roles_required(*_WRITE)
@module_required("delivery_tracking")
@permission_required(PERM_BILLING)
def create_furniture_delivery():
    return delivery_controller.create_delivery()


@furniture_bp.patch("/deliveries/<delivery_id>/status")
@roles_required(*_WRITE)
@module_required("delivery_tracking")
@permission_required(PERM_BILLING)
def update_furniture_delivery_status(delivery_id):
    return delivery_controller.update_delivery_status(delivery_id)


@furniture_bp.post("/installations")
@roles_required(*_WRITE)
@module_required("installation")
@permission_required(PERM_BILLING)
def create_furniture_installation():
    return installation_controller.create_installation()


@furniture_bp.get("/quotations")
@roles_required(*_STAFF)
@module_required("quotation")
@permission_required(PERM_BILLING)
def list_furniture_quotations():
    return quotation_controller.list_quotations()


@furniture_bp.post("/quotations")
@roles_required(*_WRITE)
@module_required("quotation")
@permission_required(PERM_BILLING)
def create_furniture_quotation():
    return quotation_controller.create_quotation()


@furniture_bp.get("/quotations/<quotation_id>")
@roles_required(*_STAFF)
@module_required("quotation")
@permission_required(PERM_BILLING)
def get_furniture_quotation(quotation_id):
    return quotation_controller.get_quotation(quotation_id)


@furniture_bp.patch("/quotations/<quotation_id>/status")
@roles_required(*_WRITE)
@module_required("quotation")
@permission_required(PERM_BILLING)
def update_furniture_quotation_status(quotation_id):
    return quotation_controller.update_quotation_status(quotation_id)


@furniture_bp.post("/quotations/<quotation_id>/convert")
@roles_required(*_WRITE)
@module_required("quotation")
@permission_required(PERM_BILLING)
def convert_furniture_quotation(quotation_id):
    return quotation_controller.convert_quotation(quotation_id)
