"""Supplier data access — tenant scoped."""

from sqlalchemy import func, or_

from app.extensions import db
from app.models.supplier import Supplier


class SupplierRepository:
    @staticmethod
    def get_by_id_and_tenant(supplier_id: str, tenant_id: str) -> Supplier | None:
        return (
            db.session.query(Supplier)
            .filter(Supplier.id == supplier_id, Supplier.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def find_by_phone_e164(tenant_id: str, phone_e164: str) -> Supplier | None:
        if not phone_e164:
            return None
        return (
            db.session.query(Supplier)
            .filter(Supplier.tenant_id == tenant_id, Supplier.phone_e164 == phone_e164)
            .first()
        )

    @staticmethod
    def find_by_gstin(tenant_id: str, gstin: str) -> Supplier | None:
        if not gstin:
            return None
        return (
            db.session.query(Supplier)
            .filter(Supplier.tenant_id == tenant_id, Supplier.gstin == gstin)
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
    ) -> tuple[list[Supplier], int]:
        query = db.session.query(Supplier).filter(Supplier.tenant_id == tenant_id)
        if is_active is not None:
            query = query.filter(Supplier.is_active.is_(bool(is_active)))
        if q:
            term = q.strip()
            like = f"%{term}%"
            digits = "".join(ch for ch in term if ch.isdigit())
            filters = [
                Supplier.name.ilike(like),
                Supplier.email.ilike(like),
                Supplier.gstin.ilike(like),
                Supplier.phone_national.ilike(like),
                Supplier.address.ilike(like),
            ]
            if digits:
                filters.append(Supplier.phone_national.ilike(f"%{digits}%"))
                filters.append(Supplier.phone_e164.ilike(f"%{digits}%"))
            query = query.filter(or_(*filters))
        total = query.with_entities(func.count(Supplier.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(Supplier.name.asc(), Supplier.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def add(supplier: Supplier) -> Supplier:
        db.session.add(supplier)
        return supplier
