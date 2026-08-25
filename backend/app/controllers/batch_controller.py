"""Batch / expiry HTTP controller (BIZ-22)."""

from flask import request

from app.schemas.item_batch_schemas import adjust_batch_schema, create_batch_schema
from app.services.batch_service import BatchService
from app.utils.responses import success_response


def list_batches():
    item_id = request.args.get("item_id")
    status = request.args.get("status")
    within_days = request.args.get("within_days", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    data, meta = BatchService.list_batches(
        item_id=item_id,
        status=status,
        within_days=within_days,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def expiry_report():
    within_days = request.args.get("within_days", 7, type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    return success_response(
        data=BatchService.expiry_report(
            within_days=within_days, page=page, per_page=per_page
        )
    )


def create_batch():
    payload = create_batch_schema.load(request.get_json() or {})
    data = BatchService.create_batch(
        item_id=payload["item_id"],
        quantity=payload["quantity"],
        expiry_date=payload["expiry_date"],
        batch_code=payload.get("batch_code"),
        reason=payload.get("reason"),
    )
    return success_response(data=data, status_code=201)


def adjust_batch(batch_id: str):
    payload = adjust_batch_schema.load(request.get_json() or {})
    data = BatchService.adjust_batch(
        batch_id,
        delta=payload["delta"],
        reason=payload["reason"],
    )
    return success_response(data=data)
