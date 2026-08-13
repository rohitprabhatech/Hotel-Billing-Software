"""Bill HTTP controller."""

from flask import request

from app.schemas.bill_schemas import cancel_bill_schema, create_bill_schema
from app.services.bill_service import BillService
from app.utils.responses import success_response


def create_bill():
    payload = create_bill_schema.load(request.get_json() or {})
    data = BillService.create_bill(
        items=payload["items"],
        discount=payload.get("discount", 0),
        table_number=payload.get("table_number"),
        payment_method=payload.get("payment_method"),
    )
    return success_response(data=data, status_code=201)


def list_bills():
    status = request.args.get("status")
    q = request.args.get("q")
    payment_method = request.args.get("payment_method")
    today_only = str(request.args.get("today", "")).lower() in {"1", "true", "yes"}
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = BillService.list_bills(
        status=status,
        page=page,
        per_page=per_page,
        today_only=today_only,
        q=q,
        payment_method=payment_method,
    )
    return success_response(data=data, meta=meta)


def get_bill(bill_id: str):
    return success_response(data=BillService.get_bill(bill_id))


def today_summary():
    return success_response(data=BillService.today_summary())


def cancel_bill(bill_id: str):
    payload = cancel_bill_schema.load(request.get_json() or {})
    data = BillService.cancel_bill(bill_id, payload["reason"])
    return success_response(data=data)


def print_bill(bill_id: str):
    data = BillService.record_print(bill_id)
    return success_response(data=data)