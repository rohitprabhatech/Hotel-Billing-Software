"""Purchase order HTTP controller (BIZ-52)."""

from flask import request

from app.schemas.order_document_schemas import (
    convert_purchase_order_schema,
    create_purchase_order_schema,
    update_purchase_order_status_schema,
)
from app.services.purchase_order_service import PurchaseOrderService
from app.utils.responses import success_response


def list_purchase_orders():
    data, meta = PurchaseOrderService.list_orders(
        status=request.args.get("status"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_purchase_order(order_id: str):
    return success_response(data=PurchaseOrderService.get(order_id))


def create_purchase_order():
    payload = create_purchase_order_schema.load(request.get_json() or {})
    data = PurchaseOrderService.create(
        items=payload["items"],
        supplier_id=payload.get("supplier_id"),
        notes=payload.get("notes"),
        expected_date=payload.get("expected_date"),
    )
    return success_response(data=data, status_code=201)


def update_purchase_order_status(order_id: str):
    payload = update_purchase_order_status_schema.load(request.get_json() or {})
    data = PurchaseOrderService.update_status(
        order_id, status=payload["status"], notes=payload.get("notes")
    )
    return success_response(data=data)


def convert_purchase_order(order_id: str):
    payload = convert_purchase_order_schema.load(request.get_json() or {})
    data = PurchaseOrderService.convert_to_purchase(
        order_id,
        payment_method=payload.get("payment_method") or "cash",
        invoice_number=payload.get("invoice_number"),
    )
    return success_response(data=data)
