"""Travel booking detail HTTP controller (BIZ-58)."""

from flask import request

from app.schemas.travel_booking_detail_schemas import (
    create_booking_document_schema,
    create_itinerary_item_schema,
    update_itinerary_item_schema,
)
from app.services.travel_booking_detail_service import TravelBookingDetailService
from app.utils.responses import success_response


def list_itinerary(booking_id: str):
    return success_response(data=TravelBookingDetailService.list_itinerary(booking_id))


def create_itinerary(booking_id: str):
    payload = create_itinerary_item_schema.load(request.get_json() or {})
    data = TravelBookingDetailService.create_itinerary(booking_id, **payload)
    return success_response(data=data, status_code=201)


def update_itinerary(booking_id: str, item_id: str):
    raw = request.get_json() or {}
    payload = update_itinerary_item_schema.load(raw)
    # Only apply keys the client sent (avoid wipe from schema defaults).
    fields = {key: payload[key] for key in payload if key in raw}
    data = TravelBookingDetailService.update_itinerary(booking_id, item_id, **fields)
    return success_response(data=data)


def delete_itinerary(booking_id: str, item_id: str):
    return success_response(
        data=TravelBookingDetailService.delete_itinerary(booking_id, item_id)
    )


def list_documents(booking_id: str):
    return success_response(data=TravelBookingDetailService.list_documents(booking_id))


def create_document(booking_id: str):
    payload = create_booking_document_schema.load(request.get_json() or {})
    data = TravelBookingDetailService.create_document(booking_id, **payload)
    return success_response(data=data, status_code=201)


def delete_document(booking_id: str, document_id: str):
    return success_response(
        data=TravelBookingDetailService.delete_document(booking_id, document_id)
    )
