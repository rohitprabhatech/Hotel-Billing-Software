"""Serial unit HTTP controller (BIZ-29)."""

from flask import request

from app.schemas.serial_unit_schemas import receive_serial_schema
from app.services.serial_service import SerialService
from app.utils.responses import success_response


def list_units():
    data, meta = SerialService.list_units(
        item_id=request.args.get("item_id"),
        status=request.args.get("status"),
        q=request.args.get("q"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def get_by_serial(serial: str):
    return success_response(data=SerialService.get_by_serial(serial))


def receive():
    payload = receive_serial_schema.load(request.get_json() or {})
    data = SerialService.receive(
        item_id=payload["item_id"],
        serial=payload["serial"],
        warranty_months=payload.get("warranty_months"),
    )
    return success_response(data=data, status_code=201)
