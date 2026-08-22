"""Wastage HTTP controller (BIZ-18)."""

from flask import request

from app.schemas.wastage_schemas import create_wastage_schema
from app.services.wastage_service import WastageService
from app.utils.responses import success_response


def list_wastage():
    item_id = request.args.get("item_id")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = WastageService.list_wastage(
        item_id=item_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_wastage(wastage_id: str):
    return success_response(data=WastageService.get_wastage(wastage_id))


def create_wastage():
    payload = create_wastage_schema.load(request.get_json() or {})
    data = WastageService.create_wastage(
        item_id=payload["item_id"],
        quantity=payload["quantity"],
        reason=payload.get("reason"),
        category=payload.get("category"),
        wastage_date=payload.get("wastage_date"),
    )
    return success_response(data=data, status_code=201)
