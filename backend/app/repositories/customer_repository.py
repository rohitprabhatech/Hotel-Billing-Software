"""Customer data access — tenant scoped."""

from sqlalchemy import func, or_

from app.extensions import db
from app.models.customer import Customer


class CustomerRepository:
    @staticmethod
    def get_by_id_and_tenant(customer_id: str, tenant_id: str) -> Customer | None:
        return (
            db.session.query(Customer)
            .filter(Customer.id == customer_id, Customer.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def find_by_phone_e164(tenant_id: str, phone_e164: str) -> Customer | None:
        if not phone_e164:
            return None
        return (
            db.session.query(Customer)
            .filter(Customer.tenant_id == tenant_id, Customer.phone_e164 == phone_e164)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        q: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Customer], int]:
        query = db.session.query(Customer).filter(Customer.tenant_id == tenant_id)
        if is_active is not None:
            query = query.filter(Customer.is_active.is_(bool(is_active)))
        if q:
            term = q.strip()
            like = f"%{term}%"
            digits = "".join(ch for ch in term if ch.isdigit())
            filters = [
                Customer.name.ilike(like),
                Customer.email.ilike(like),
                Customer.phone_national.ilike(like),
            ]
            if digits:
                filters.append(Customer.phone_national.ilike(f"%{digits}%"))
                filters.append(Customer.phone_e164.ilike(f"%{digits}%"))
            query = query.filter(or_(*filters))
        total = query.with_entities(func.count(Customer.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(Customer.name.asc(), Customer.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def add(customer: Customer) -> Customer:
        db.session.add(customer)
        return customer
