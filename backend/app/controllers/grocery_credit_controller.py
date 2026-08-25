"""Grocery credit HTTP controller (BIZ-23)."""

from flask import request

from app.schemas.party_ledger_schemas import customer_payment_schema
from app.services.grocery_credit_service import GroceryCreditService
from app.utils.responses import success_response


def list_outstanding():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = GroceryCreditService.list_outstanding(page=page, per_page=per_page)
    return success_response(data=data, meta=meta)


def customer_credit(customer_id: str):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = GroceryCreditService.customer_credit(
        customer_id, page=page, per_page=per_page
    )
    return success_response(data=data, meta=meta)


def record_payment(customer_id: str):
    payload = customer_payment_schema.load(request.get_json() or {})
    data = GroceryCreditService.record_payment(
        customer_id,
        amount=payload["amount"],
        notes=payload.get("notes"),
        collection_method=payload.get("collection_method"),
    )
    return success_response(data=data, status_code=201)


def sales_report():
    date = request.args.get("date")
    payment_method = request.args.get("payment_method")
    data = GroceryCreditService.sales_report(date=date, payment_method=payment_method)
    return success_response(data=data)
