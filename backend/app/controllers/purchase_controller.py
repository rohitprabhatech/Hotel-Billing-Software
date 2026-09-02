"""Purchase HTTP controller."""

from flask import request

from app.schemas.purchase_schemas import cancel_purchase_schema, create_purchase_schema, update_purchase_schema
from app.services.purchase_service import PurchaseService
from app.utils.responses import success_response


def list_purchases():
    status = request.args.get("status")
    supplier_id = request.args.get("supplier_id")
    q = request.args.get("q")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = PurchaseService.list_purchases(
        status=status,
        supplier_id=supplier_id,
        q=q,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_purchase(purchase_id: str):
    return success_response(data=PurchaseService.get_purchase(purchase_id))


def create_purchase():
    payload = create_purchase_schema.load(request.get_json() or {})
    data = PurchaseService.create_purchase(
        supplier_id=payload.get("supplier_id"),
        invoice_number=payload.get("invoice_number"),
        notes=payload.get("notes"),
        items=payload["items"],
        payment_method=payload.get("payment_method") or "cash",
    )
    return success_response(data=data, status_code=201)


def update_purchase(purchase_id: str):
    payload = update_purchase_schema.load(request.get_json() or {})
    data = PurchaseService.update_purchase(purchase_id, **payload)
    return success_response(data=data)


def cancel_purchase(purchase_id: str):
    payload = cancel_purchase_schema.load(request.get_json() or {})
    data = PurchaseService.cancel_purchase(purchase_id, payload["reason"])
    return success_response(data=data)
