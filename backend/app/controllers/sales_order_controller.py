"""Sales order HTTP controller (BIZ-52)."""

from flask import request

from app.schemas.order_document_schemas import (
    convert_sales_order_schema,
    create_sales_order_schema,
    update_sales_order_status_schema,
)
from app.services.sales_order_service import SalesOrderService
from app.utils.responses import success_response


def list_sales_orders():
    data, meta = SalesOrderService.list_orders(
        status=request.args.get("status"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_sales_order(order_id: str):
    return success_response(data=SalesOrderService.get(order_id))


def create_sales_order():
    payload = create_sales_order_schema.load(request.get_json() or {})
    data = SalesOrderService.create(
        items=payload["items"],
        customer_id=payload.get("customer_id"),
        customer_name=payload.get("customer_name"),
        customer_phone=payload.get("customer_phone"),
        notes=payload.get("notes"),
        discount=payload.get("discount") or 0,
        expected_delivery_date=payload.get("expected_delivery_date"),
    )
    return success_response(data=data, status_code=201)


def update_sales_order_status(order_id: str):
    payload = update_sales_order_status_schema.load(request.get_json() or {})
    data = SalesOrderService.update_status(
        order_id, status=payload["status"], notes=payload.get("notes")
    )
    return success_response(data=data)


def convert_sales_order(order_id: str):
    payload = convert_sales_order_schema.load(request.get_json() or {})
    data = SalesOrderService.convert_to_bill(
        order_id, payment_method=payload.get("payment_method")
    )
    return success_response(data=data)
