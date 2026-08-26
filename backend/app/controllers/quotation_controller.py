"""Quotation HTTP controller (BIZ-36)."""

from flask import request

from app.schemas.quotation_schemas import (
    convert_quotation_schema,
    create_quotation_schema,
    update_quotation_status_schema,
)
from app.services.quotation_service import QuotationService
from app.utils.responses import success_response


def list_quotations():
    data, meta = QuotationService.list_quotations(
        status=request.args.get("status"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_quotation(quotation_id: str):
    return success_response(data=QuotationService.get(quotation_id))


def create_quotation():
    payload = create_quotation_schema.load(request.get_json() or {})
    data = QuotationService.create(
        items=payload["items"],
        customer_id=payload.get("customer_id"),
        customer_name=payload.get("customer_name"),
        customer_phone=payload.get("customer_phone"),
        notes=payload.get("notes"),
        discount=payload.get("discount") or 0,
        valid_until=payload.get("valid_until"),
    )
    return success_response(data=data, status_code=201)


def update_quotation_status(quotation_id: str):
    payload = update_quotation_status_schema.load(request.get_json() or {})
    data = QuotationService.update_status(
        quotation_id,
        status=payload["status"],
        notes=payload.get("notes"),
    )
    return success_response(data=data)


def convert_quotation(quotation_id: str):
    payload = convert_quotation_schema.load(request.get_json() or {})
    data = QuotationService.convert_to_bill(
        quotation_id, payment_method=payload.get("payment_method")
    )
    return success_response(data=data)
