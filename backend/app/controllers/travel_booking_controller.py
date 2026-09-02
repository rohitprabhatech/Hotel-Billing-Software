"""Travel booking HTTP controller (BIZ-57)."""

from flask import request

from app.schemas.travel_booking_schemas import (
    create_travel_booking_schema,
    record_travel_booking_payment_schema,
    update_travel_booking_schema,
    update_travel_booking_status_schema,
)
from app.services.travel_booking_service import TravelBookingService
from app.utils.responses import success_response


def list_bookings():
    data, meta = TravelBookingService.list_bookings(
        status=request.args.get("status"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def get_booking(booking_id: str):
    return success_response(data=TravelBookingService.get_booking(booking_id))


def create_booking():
    payload = create_travel_booking_schema.load(request.get_json() or {})
    data = TravelBookingService.create(**payload)
    return success_response(data=data, status_code=201)


def update_booking_status(booking_id: str):
    payload = update_travel_booking_status_schema.load(request.get_json() or {})
    data = TravelBookingService.update_status(booking_id, status=payload["status"])
    return success_response(data=data)


def update_booking(booking_id: str):
    payload = update_travel_booking_schema.load(request.get_json() or {})
    data = TravelBookingService.update_booking(booking_id, **payload)
    return success_response(data=data)


def delete_booking(booking_id: str):
    data = TravelBookingService.delete_booking(booking_id)
    return success_response(data=data)


def record_payment(booking_id: str):
    payload = record_travel_booking_payment_schema.load(request.get_json() or {})
    data = TravelBookingService.record_payment(booking_id=booking_id, **payload)
    return success_response(data=data, status_code=201)
