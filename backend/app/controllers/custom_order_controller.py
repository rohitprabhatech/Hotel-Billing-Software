"""Custom order HTTP controller (BIZ-42)."""

from flask import request

from app.schemas.custom_order_schemas import (
    create_custom_order_schema,
    record_advance_schema,
    update_custom_order_status_schema,
)
from app.services.custom_order_service import CustomOrderService
from app.utils.responses import success_response


def list_orders():
    order_type = request.args.get("order_type")
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    data, meta = CustomOrderService.list_orders(
        order_type=order_type,
        status=status,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_order(order_id: str):
    return success_response(data=CustomOrderService.get_order(order_id))


def create_order():
    payload = create_custom_order_schema.load(request.get_json() or {})
    data = CustomOrderService.create(
        order_type=payload.get("order_type") or "bakery",
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


def update_status(order_id: str):
    payload = update_custom_order_status_schema.load(request.get_json() or {})
    data = CustomOrderService.update_status(
        order_id,
        status=payload["status"],
        notes=payload.get("notes"),
    )
    return success_response(data=data)


def record_advance(order_id: str):
    payload = record_advance_schema.load(request.get_json() or {})
    data = CustomOrderService.record_advance(
        order_id=order_id,
        amount=payload["amount"],
        payment_method=payload.get("payment_method") or "cash",
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)
