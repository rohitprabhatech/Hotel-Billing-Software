"""Bakery convenience routes (BIZ-41 / BIZ-42)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING, PERM_ITEMS_READ
from app.controllers import batch_controller, custom_order_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

bakery_bp = Blueprint("bakery", __name__, url_prefix="/bakery")

_STAFF = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@bakery_bp.get("/expiry")
@roles_required(*_STAFF)
@module_required("batch_expiry")
@permission_required(PERM_ITEMS_READ)
def bakery_expiry():
    """Alias for GET /batches/expiry (bakery finished-goods expiry)."""
    return batch_controller.expiry_report()


@bakery_bp.get("/cake-orders")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def list_cake_orders():
    from flask import request

    # Force bakery type for this alias.
    args = request.args.to_dict(flat=True)
    args["order_type"] = "bakery"
    request.args = type(request.args).from_keys(args) if False else request.args
    # Prefer mutating via controller kwargs path:
    from app.services.custom_order_service import CustomOrderService
    from app.utils.responses import success_response

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    status = request.args.get("status")
    data, meta = CustomOrderService.list_orders(
        order_type="bakery",
        status=status,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


@bakery_bp.post("/cake-orders")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def create_cake_order():
    from flask import request

    from app.schemas.custom_order_schemas import create_custom_order_schema
    from app.services.custom_order_service import CustomOrderService
    from app.utils.responses import success_response

    payload = create_custom_order_schema.load(request.get_json() or {})
    data = CustomOrderService.create(
        order_type="bakery",
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


@bakery_bp.post("/cake-orders/<order_id>/advance")
@roles_required(*_STAFF)
@module_required("custom_orders")
@permission_required(PERM_BILLING)
def cake_order_advance(order_id):
    return custom_order_controller.record_advance(order_id)
