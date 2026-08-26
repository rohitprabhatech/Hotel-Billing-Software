"""Repair order HTTP controller (BIZ-31)."""

from flask import request

from app.schemas.repair_schemas import create_repair_schema, update_repair_status_schema
from app.services.repair_service import RepairService
from app.utils.responses import success_response


def list_repairs():
    data, meta = RepairService.list_orders(
        status=request.args.get("status"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_repair(repair_id: str):
    return success_response(data=RepairService.get_order(repair_id))


def create_repair():
    payload = create_repair_schema.load(request.get_json() or {})
    data = RepairService.create(
        serial_unit_id=payload["serial_unit_id"],
        issue_description=payload["issue_description"],
        customer_name=payload.get("customer_name"),
        customer_phone=payload.get("customer_phone"),
        bill_id=payload.get("bill_id"),
        notes=payload.get("notes"),
        estimated_charge=payload.get("estimated_charge"),
    )
    return success_response(data=data, status_code=201)


def update_repair_status(repair_id: str):
    payload = update_repair_status_schema.load(request.get_json() or {})
    data = RepairService.update_status(
        repair_id,
        status=payload["status"],
        notes=payload.get("notes"),
    )
    return success_response(data=data)
