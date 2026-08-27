"""KOT data access — tenant scoped."""

from sqlalchemy import func
from sqlalchemy.orm import joinedload, noload

from app.constants.kots import ACTIVE_KOT_STATUSES
from app.extensions import db
from app.models.kot import Kot, KotItem, KotNumberCounter


class KotRepository:
    @staticmethod
    def get_by_id_and_tenant(kot_id: str, tenant_id: str) -> Kot | None:
        return (
            db.session.query(Kot)
            .options(
                joinedload(Kot.items),
                joinedload(Kot.dining_table),
                joinedload(Kot.creator),
                joinedload(Kot.order),
            )
            .filter(Kot.id == kot_id, Kot.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def get_active_by_order(tenant_id: str, order_id: str) -> Kot | None:
        return (
            db.session.query(Kot)
            .options(joinedload(Kot.items))
            .filter(
                Kot.tenant_id == tenant_id,
                Kot.order_id == order_id,
                Kot.status.in_(ACTIVE_KOT_STATUSES),
            )
            .order_by(Kot.created_at.desc())
            .first()
        )

    @staticmethod
    def get_latest_by_order(tenant_id: str, order_id: str) -> Kot | None:
        return (
            db.session.query(Kot)
            .options(joinedload(Kot.items))
            .filter(Kot.tenant_id == tenant_id, Kot.order_id == order_id)
            .order_by(Kot.created_at.desc())
            .first()
        )

    @staticmethod
    def sum_sent_qty_by_order_item(tenant_id: str, order_id: str) -> dict[str, float]:
        """Total quantity already ticketed per order_item_id for an order."""
        rows = (
            db.session.query(KotItem.order_item_id, func.sum(KotItem.quantity))
            .join(Kot, Kot.id == KotItem.kot_id)
            .filter(
                KotItem.tenant_id == tenant_id,
                Kot.tenant_id == tenant_id,
                Kot.order_id == order_id,
                KotItem.order_item_id.isnot(None),
            )
            .group_by(KotItem.order_item_id)
            .all()
        )
        return {order_item_id: float(total or 0) for order_item_id, total in rows}

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        status: str | None = None,
        statuses: list[str] | None = None,
        order_id: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Kot], int]:
        query = db.session.query(Kot).filter(Kot.tenant_id == tenant_id)
        if status:
            query = query.filter(Kot.status == status)
        if statuses:
            query = query.filter(Kot.status.in_(statuses))
        if order_id:
            query = query.filter(Kot.order_id == order_id)
        total = query.with_entities(func.count(Kot.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.options(
                noload(Kot.items),
                joinedload(Kot.dining_table),
                joinedload(Kot.creator),
            )
            .order_by(Kot.created_at.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def list_kitchen_queue(tenant_id: str) -> list[Kot]:
        return (
            db.session.query(Kot)
            .options(joinedload(Kot.items), joinedload(Kot.dining_table))
            .filter(
                Kot.tenant_id == tenant_id,
                Kot.status.in_(ACTIVE_KOT_STATUSES),
            )
            .order_by(Kot.created_at.asc())
            .all()
        )

    @staticmethod
    def allocate_kot_number(tenant_id: str, prefix: str | None = "KOT-") -> tuple[int, str]:
        counter = (
            db.session.query(KotNumberCounter)
            .filter(KotNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = KotNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()

        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        label = f"{prefix or ''}{sequence}"
        return sequence, label

    @staticmethod
    def count_items_by_kot_ids(tenant_id: str, kot_ids: list[str]) -> dict[str, int]:
        if not kot_ids:
            return {}
        rows = (
            db.session.query(KotItem.kot_id, func.count(KotItem.id))
            .filter(KotItem.tenant_id == tenant_id, KotItem.kot_id.in_(kot_ids))
            .group_by(KotItem.kot_id)
            .all()
        )
        return {kot_id: int(count) for kot_id, count in rows}

    @staticmethod
    def add(kot: Kot) -> Kot:
        db.session.add(kot)
        return kot
