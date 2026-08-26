"""Travel itinerary + document metadata access (BIZ-58)."""

from app.extensions import db
from app.models.travel_booking_detail import TravelBookingDocument, TravelItineraryItem


class TravelBookingDetailRepository:
    @staticmethod
    def get_itinerary_item(
        tenant_id: str, booking_id: str, item_id: str
    ) -> TravelItineraryItem | None:
        return TravelItineraryItem.query.filter_by(
            tenant_id=tenant_id, booking_id=booking_id, id=item_id
        ).first()

    @staticmethod
    def list_itinerary(tenant_id: str, booking_id: str) -> list[TravelItineraryItem]:
        return (
            TravelItineraryItem.query.filter_by(tenant_id=tenant_id, booking_id=booking_id)
            .order_by(
                TravelItineraryItem.sort_order.asc(),
                TravelItineraryItem.day_number.asc(),
                TravelItineraryItem.created_at.asc(),
            )
            .all()
        )

    @staticmethod
    def add_itinerary(row: TravelItineraryItem) -> TravelItineraryItem:
        db.session.add(row)
        return row

    @staticmethod
    def delete_itinerary(row: TravelItineraryItem) -> None:
        db.session.delete(row)

    @staticmethod
    def get_document(
        tenant_id: str, booking_id: str, document_id: str
    ) -> TravelBookingDocument | None:
        return TravelBookingDocument.query.filter_by(
            tenant_id=tenant_id, booking_id=booking_id, id=document_id
        ).first()

    @staticmethod
    def list_documents(tenant_id: str, booking_id: str) -> list[TravelBookingDocument]:
        return (
            TravelBookingDocument.query.filter_by(tenant_id=tenant_id, booking_id=booking_id)
            .order_by(TravelBookingDocument.created_at.asc())
            .all()
        )

    @staticmethod
    def add_document(row: TravelBookingDocument) -> TravelBookingDocument:
        db.session.add(row)
        return row

    @staticmethod
    def delete_document(row: TravelBookingDocument) -> None:
        db.session.delete(row)
