"""Production run data access (BIZ-40)."""

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.production_run import (
    ProductionRun,
    ProductionRunItem,
    ProductionRunNumberCounter,
)


class ProductionRunRepository:
    @staticmethod
    def get_by_id_and_tenant(run_id: str, tenant_id: str) -> ProductionRun | None:
        return (
            db.session.query(ProductionRun)
            .options(joinedload(ProductionRun.items))
            .filter(ProductionRun.id == run_id, ProductionRun.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        finished_item_id: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[ProductionRun], int]:
        query = db.session.query(ProductionRun).filter(ProductionRun.tenant_id == tenant_id)
        if finished_item_id:
            query = query.filter(ProductionRun.finished_item_id == finished_item_id)
        if from_date:
            query = query.filter(ProductionRun.run_date >= from_date)
        if to_date:
            query = query.filter(ProductionRun.run_date <= to_date)
        total = query.with_entities(func.count(ProductionRun.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.options(joinedload(ProductionRun.items))
            .order_by(ProductionRun.run_date.desc(), ProductionRun.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(ProductionRunNumberCounter)
            .filter(ProductionRunNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = ProductionRunNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"PR-{sequence:05d}"

    @staticmethod
    def add(run: ProductionRun) -> ProductionRun:
        db.session.add(run)
        return run

    @staticmethod
    def add_item(row: ProductionRunItem) -> ProductionRunItem:
        db.session.add(row)
        return row
