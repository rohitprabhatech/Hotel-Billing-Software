"""Order HTTP controller (BIZ-13)."""

from flask import request

from app.schemas.order_schemas import (
    add_order_item_schema,
    cancel_order_schema,
    create_order_schema,
    update_order_item_schema,
    update_order_schema,
)
from app.services.order_service import OrderService
from app.utils.responses import success_response


def list_orders():
    status = request.args.get("status")
    channel = request.args.get("channel")
    dining_table_id = request.args.get("dining_table_id")
    q = request.args.get("q")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = OrderService.list_orders(
        status=status,
        channel=channel,
        dining_table_id=dining_table_id,
        q=q,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_order(order_id: str):
    return success_response(data=OrderService.get_order(order_id))


def create_order():
    payload = create_order_schema.load(request.get_json() or {})
    data = OrderService.create_order(
        channel=payload["channel"],
        dining_table_id=payload.get("dining_table_id"),
        customer_id=payload.get("customer_id"),
        customer_name=payload.get("customer_name"),
        customer_phone_country_code=payload.get("customer_phone_country_code"),
        customer_phone=payload.get("customer_phone"),
        delivery_address=payload.get("delivery_address"),
        notes=payload.get("notes"),
        items=payload.get("items") or [],
        combos=payload.get("combos") or [],
    )
    return success_response(data=data, status_code=201)


def update_order(order_id: str):
    raw = request.get_json() or {}
    update_order_schema.load(raw)
    data = OrderService.update_order(
        order_id,
        customer_id=raw.get("customer_id") if "customer_id" in raw else None,
        customer_name=raw.get("customer_name") if "customer_name" in raw else None,
        customer_phone_country_code=(
            raw.get("customer_phone_country_code") if "customer_phone_country_code" in raw else None
        ),
        customer_phone=raw.get("customer_phone") if "customer_phone" in raw else None,
        delivery_address=raw.get("delivery_address") if "delivery_address" in raw else None,
        notes=raw.get("notes") if "notes" in raw else None,
        customer_id_provided="customer_id" in raw,
        customer_name_provided="customer_name" in raw,
        customer_phone_provided="customer_phone_country_code" in raw or "customer_phone" in raw,
        delivery_address_provided="delivery_address" in raw,
        notes_provided="notes" in raw,
    )
    return success_response(data=data)


def add_order_item(order_id: str):
    payload = add_order_item_schema.load(request.get_json() or {})
    data = OrderService.add_item(
        order_id,
        item_id=payload["item_id"],
        quantity=payload["quantity"],
        addon_ids=payload.get("addon_ids") or [],
    )
    return success_response(data=data, status_code=201)


def update_order_item(order_id: str, line_id: str):
    payload = update_order_item_schema.load(request.get_json() or {})
    data = OrderService.update_item(order_id, line_id, quantity=payload["quantity"])
    return success_response(data=data)


def remove_order_item(order_id: str, line_id: str):
    data = OrderService.remove_item(order_id, line_id)
    return success_response(data=data)


def cancel_order(order_id: str):
    payload = cancel_order_schema.load(request.get_json() or {})
    data = OrderService.cancel_order(order_id, reason=payload.get("reason"))
    return success_response(data=data)
