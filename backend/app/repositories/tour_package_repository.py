"""Tour package data access (BIZ-56)."""

from sqlalchemy import func

from app.extensions import db
from app.models.tour_package import TourPackage


class TourPackageRepository:
    @staticmethod
    def get_by_id(tenant_id: str, package_id: str) -> TourPackage | None:
        return TourPackage.query.filter_by(tenant_id=tenant_id, id=package_id).first()

    @staticmethod
    def get_by_code(tenant_id: str, code: str) -> TourPackage | None:
        return TourPackage.query.filter_by(tenant_id=tenant_id, code=code).first()

    @staticmethod
    def get_by_item_id(tenant_id: str, item_id: str) -> TourPackage | None:
        return TourPackage.query.filter_by(tenant_id=tenant_id, item_id=item_id).first()

    @staticmethod
    def add(row: TourPackage) -> TourPackage:
        db.session.add(row)
        return row

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        active_only: bool = False,
        q: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[TourPackage], int]:
        query = TourPackage.query.filter_by(tenant_id=tenant_id)
        if active_only:
            query = query.filter_by(is_active=True)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                db.or_(
                    TourPackage.name.ilike(like),
                    TourPackage.code.ilike(like),
                    TourPackage.destination.ilike(like),
                )
            )
        total = query.with_entities(func.count(TourPackage.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(TourPackage.name.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)
