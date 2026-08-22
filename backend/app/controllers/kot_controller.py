"""KOT HTTP controller (BIZ-14)."""

from flask import request

from app.schemas.kot_schemas import update_kot_status_schema
from app.services.kot_service import KotService
from app.utils.responses import success_response


def list_kots():
    status = request.args.get("status")
    order_id = request.args.get("order_id")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = KotService.list_kots(
        status=status,
        order_id=order_id,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_kitchen_queue():
    return success_response(data=KotService.get_kitchen_queue())


def get_kot(kot_id: str):
    return success_response(data=KotService.get_kot(kot_id))


def update_kot_status(kot_id: str):
    payload = update_kot_status_schema.load(request.get_json() or {})
    data = KotService.update_status(kot_id, status=payload["status"])
    return success_response(data=data)


def fire_kot_for_order(order_id: str):
    data = KotService.fire_kot_for_order(order_id)
    return success_response(data=data, status_code=201)
