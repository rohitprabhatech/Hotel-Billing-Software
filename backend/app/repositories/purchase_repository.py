"""Purchase data access — tenant scoped."""

from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload, noload

from app.extensions import db
from app.models.purchase import Purchase, PurchaseItem, PurchaseNumberCounter


class PurchaseRepository:
    @staticmethod
    def get_by_id_and_tenant(purchase_id: str, tenant_id: str) -> Purchase | None:
        return (
            db.session.query(Purchase)
            .options(joinedload(Purchase.items), joinedload(Purchase.supplier), joinedload(Purchase.creator))
            .filter(Purchase.id == purchase_id, Purchase.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        status: str | None = None,
        supplier_id: str | None = None,
        q: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Purchase], int]:
        query = db.session.query(Purchase).filter(Purchase.tenant_id == tenant_id)
        if status:
            query = query.filter(Purchase.status == status)
        if supplier_id:
            query = query.filter(Purchase.supplier_id == supplier_id)
        if date_from:
            query = query.filter(Purchase.created_at >= date_from)
        if date_to:
            query = query.filter(Purchase.created_at <= date_to)
        if q:
            term = q.strip()
            like = f"%{term}%"
            query = query.filter(
                or_(
                    Purchase.purchase_number.ilike(like),
                    Purchase.invoice_number.ilike(like),
                    Purchase.supplier_name.ilike(like),
                )
            )
        total = query.with_entities(func.count(Purchase.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.options(noload(Purchase.items), joinedload(Purchase.creator), joinedload(Purchase.supplier))
            .order_by(Purchase.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_purchase_number(tenant_id: str, prefix: str | None = "PO-") -> tuple[int, str]:
        counter = (
            db.session.query(PurchaseNumberCounter)
            .filter(PurchaseNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = PurchaseNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()

        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()

        prefix = prefix or ""
        purchase_number = f"{prefix}{sequence}" if prefix else str(sequence)
        return sequence, purchase_number

    @staticmethod
    def add_purchase(purchase: Purchase) -> Purchase:
        db.session.add(purchase)
        return purchase

    @staticmethod
    def add_item(item: PurchaseItem) -> PurchaseItem:
        db.session.add(item)
        return item
