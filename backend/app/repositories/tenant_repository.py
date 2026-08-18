"""Tenant data access."""

from sqlalchemy import or_

from app.extensions import db
from app.models.tenant import Tenant


class TenantRepository:
    @staticmethod
    def get_by_id(tenant_id: str) -> Tenant | None:
        return db.session.get(Tenant, tenant_id)

    @staticmethod
    def count_all() -> int:
        return int(db.session.query(Tenant).count())

    @staticmethod
    def count_by_status(status: str) -> int:
        return int(db.session.query(Tenant).filter(Tenant.status == status).count())

    @staticmethod
    def list_all(*, q: str | None = None, page: int = 1, per_page: int = 25) -> tuple[list[Tenant], int]:
        query = db.session.query(Tenant)
        term = (q or "").strip()
        if term:
            like = f"%{term}%"
            query = query.filter(
                or_(
                    Tenant.business_name.ilike(like),
                    Tenant.name.ilike(like),
                    Tenant.email.ilike(like),
                )
            )
        total = query.order_by(None).count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 25), 1), 100)
        rows = (
            query.order_by(Tenant.business_name.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def add(tenant: Tenant) -> Tenant:
        db.session.add(tenant)
        return tenant

    @staticmethod
    def commit():
        db.session.commit()