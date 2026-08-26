"""Delivery job HTTP controller (BIZ-49)."""

from flask import request

from app.schemas.delivery_schemas import create_delivery_schema, update_delivery_status_schema
from app.services.delivery_service import DeliveryService
from app.utils.responses import success_response


def list_deliveries():
    data, meta = DeliveryService.list_jobs(
        status=request.args.get("status"),
        custom_order_id=request.args.get("custom_order_id"),
        from_date=request.args.get("from") or request.args.get("from_date"),
        to_date=request.args.get("to") or request.args.get("to_date"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_delivery(delivery_id: str):
    return success_response(data=DeliveryService.get_job(delivery_id))


def create_delivery():
    payload = create_delivery_schema.load(request.get_json() or {})
    data = DeliveryService.create(
        custom_order_id=payload["custom_order_id"],
        delivery_address=payload["delivery_address"],
        scheduled_at=payload.get("scheduled_at"),
        customer_name=payload.get("customer_name"),
        customer_phone=payload.get("customer_phone"),
        driver_name=payload.get("driver_name"),
        vehicle_number=payload.get("vehicle_number"),
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)


def update_delivery_status(delivery_id: str):
    payload = update_delivery_status_schema.load(request.get_json() or {})
    data = DeliveryService.update_status(
        delivery_id,
        status=payload["status"],
        notes=payload.get("notes"),
        driver_name=payload.get("driver_name"),
        vehicle_number=payload.get("vehicle_number"),
    )
    return success_response(data=data)
