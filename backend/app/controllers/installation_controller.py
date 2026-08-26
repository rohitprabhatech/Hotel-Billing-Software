"""Installation order HTTP controller (BIZ-33)."""

from flask import request

from app.schemas.installation_schemas import (
    create_installation_schema,
    update_installation_status_schema,
)
from app.services.installation_service import InstallationService
from app.utils.responses import success_response


def list_installations():
    data, meta = InstallationService.list_orders(
        status=request.args.get("status"),
        from_date=request.args.get("from") or request.args.get("from_date"),
        to_date=request.args.get("to") or request.args.get("to_date"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_installation(installation_id: str):
    return success_response(data=InstallationService.get_order(installation_id))


def create_installation():
    payload = create_installation_schema.load(request.get_json() or {})
    data = InstallationService.create(
        serial_unit_id=payload.get("serial_unit_id"),
        custom_order_id=payload.get("custom_order_id"),
        scheduled_at=payload["scheduled_at"],
        install_address=payload.get("install_address"),
        customer_name=payload.get("customer_name"),
        customer_phone=payload.get("customer_phone"),
        bill_id=payload.get("bill_id"),
        notes=payload.get("notes"),
        technician_name=payload.get("technician_name"),
        estimated_charge=payload.get("estimated_charge"),
    )
    return success_response(data=data, status_code=201)


def update_installation_status(installation_id: str):
    payload = update_installation_status_schema.load(request.get_json() or {})
    data = InstallationService.update_status(
        installation_id,
        status=payload["status"],
        notes=payload.get("notes"),
        technician_name=payload.get("technician_name"),
    )
    return success_response(data=data)
