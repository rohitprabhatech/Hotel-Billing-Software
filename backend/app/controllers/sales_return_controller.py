"""Sales return HTTP controller (BIZ-27)."""

from flask import request

from app.schemas.sales_return_schemas import create_sales_return_schema
from app.services.sales_return_service import SalesReturnService
from app.utils.responses import success_response


def lookup_bill():
    bill_number = request.args.get("bill_number")
    bill_id = request.args.get("bill_id")
    return success_response(data=SalesReturnService.lookup_bill(bill_number=bill_number, bill_id=bill_id))


def list_returns():
    bill_id = request.args.get("bill_id")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = SalesReturnService.list_returns(bill_id=bill_id, page=page, per_page=per_page)
    return success_response(data=data, meta=meta)


def get_return(return_id: str):
    return success_response(data=SalesReturnService.get_return(return_id))


def create_return():
    payload = create_sales_return_schema.load(request.get_json() or {})
    data = SalesReturnService.create(
        bill_id=payload["bill_id"],
        kind=payload.get("kind") or "RETURN",
        reason=payload["reason"],
        items=payload["items"],
    )
    return success_response(data=data, status_code=201)
