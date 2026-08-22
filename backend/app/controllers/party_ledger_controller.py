"""Party ledger HTTP controller."""

from flask import request

from app.schemas.party_ledger_schemas import customer_payment_schema
from app.services.party_ledger_service import PartyLedgerService
from app.utils.responses import success_response


def list_outstanding():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = PartyLedgerService.list_outstanding(page=page, per_page=per_page)
    return success_response(data=data, meta=meta)


def list_customer_ledger(customer_id: str):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = PartyLedgerService.list_customer_ledger(
        customer_id,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def record_customer_payment(customer_id: str):
    payload = customer_payment_schema.load(request.get_json() or {})
    data = PartyLedgerService.record_customer_payment(
        customer_id,
        amount=payload["amount"],
        notes=payload.get("notes"),
        collection_method=payload.get("collection_method"),
    )
    return success_response(data=data, status_code=201)
