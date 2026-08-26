"""Installation order persistence (BIZ-33)."""

from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models.installation_order import InstallationNumberCounter, InstallationOrder


class InstallationOrderRepository:
    @staticmethod
    def get_by_id(tenant_id: str, installation_id: str) -> InstallationOrder | None:
        return InstallationOrder.query.filter_by(tenant_id=tenant_id, id=installation_id).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 1,
        per_page: int = 100,
    ) -> tuple[list[InstallationOrder], int]:
        query = InstallationOrder.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status.upper())
        if from_date is not None:
            query = query.filter(InstallationOrder.scheduled_at >= from_date)
        if to_date is not None:
            query = query.filter(InstallationOrder.scheduled_at < to_date)
        total = query.with_entities(func.count(InstallationOrder.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 100), 1), 200)
        rows = (
            query.order_by(
                InstallationOrder.scheduled_at.is_(None),
                InstallationOrder.scheduled_at.asc(),
                InstallationOrder.created_at.desc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(InstallationNumberCounter)
            .filter(InstallationNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = InstallationNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"INS-{sequence:05d}"

    @staticmethod
    def add(row: InstallationOrder) -> InstallationOrder:
        db.session.add(row)
        return row
