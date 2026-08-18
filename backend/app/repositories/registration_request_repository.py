"""Registration request data access."""

from sqlalchemy import func

from app.extensions import db
from app.models.registration_request import REGISTRATION_PENDING, RegistrationRequest


class RegistrationRequestRepository:
    @staticmethod
    def get_by_id(request_id: str) -> RegistrationRequest | None:
        return db.session.get(RegistrationRequest, request_id)

    @staticmethod
    def find_pending_by_email(email: str) -> RegistrationRequest | None:
        if not email:
            return None
        return (
            db.session.query(RegistrationRequest)
            .filter(
                func.lower(RegistrationRequest.owner_email) == email.lower().strip(),
                RegistrationRequest.status == REGISTRATION_PENDING,
            )
            .first()
        )

    @staticmethod
    def count_by_status(status: str) -> int:
        return int(
            db.session.query(RegistrationRequest)
            .filter(RegistrationRequest.status == status)
            .count()
        )

    @staticmethod
    def list_filtered(
        *,
        status: str | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> tuple[list[RegistrationRequest], int]:
        query = db.session.query(RegistrationRequest)
        if status:
            query = query.filter(RegistrationRequest.status == status)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                (RegistrationRequest.business_name.ilike(like))
                | (RegistrationRequest.owner_name.ilike(like))
                | (RegistrationRequest.owner_email.ilike(like))
                | (RegistrationRequest.mobile.ilike(like))
            )
        total = query.order_by(None).count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        rows = (
            query.order_by(RegistrationRequest.requested_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def add(row: RegistrationRequest) -> RegistrationRequest:
        db.session.add(row)
        return row
