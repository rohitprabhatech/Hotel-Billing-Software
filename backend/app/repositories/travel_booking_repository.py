"""Travel booking data access (BIZ-57)."""

from sqlalchemy import func

from app.extensions import db
from app.models.travel_booking import (
    TravelBooking,
    TravelBookingNumberCounter,
    TravelBookingPayment,
)


class TravelBookingRepository:
    @staticmethod
    def get_by_id(tenant_id: str, booking_id: str) -> TravelBooking | None:
        return TravelBooking.query.filter_by(tenant_id=tenant_id, id=booking_id).first()

    @staticmethod
    def add(row: TravelBooking) -> TravelBooking:
        db.session.add(row)
        return row

    @staticmethod
    def add_payment(row: TravelBookingPayment) -> TravelBookingPayment:
        db.session.add(row)
        return row

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(TravelBookingNumberCounter)
            .filter_by(tenant_id=tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = TravelBookingNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
            counter = (
                db.session.query(TravelBookingNumberCounter)
                .filter_by(tenant_id=tenant_id)
                .with_for_update()
                .first()
            )
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"TB-{sequence:05d}"

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        status: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[TravelBooking], int]:
        query = TravelBooking.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status)
        total = query.with_entities(func.count(TravelBooking.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(TravelBooking.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)
