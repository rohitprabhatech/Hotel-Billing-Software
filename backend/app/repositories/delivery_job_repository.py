"""Delivery job persistence (BIZ-49)."""

from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models.delivery_job import (
    ACTIVE_DELIVERY_STATUSES,
    DeliveryJob,
    DeliveryNumberCounter,
)


class DeliveryJobRepository:
    @staticmethod
    def get_by_id(tenant_id: str, delivery_id: str) -> DeliveryJob | None:
        return DeliveryJob.query.filter_by(tenant_id=tenant_id, id=delivery_id).first()

    @staticmethod
    def find_active_for_custom_order(tenant_id: str, custom_order_id: str) -> DeliveryJob | None:
        return (
            DeliveryJob.query.filter(
                DeliveryJob.tenant_id == tenant_id,
                DeliveryJob.custom_order_id == custom_order_id,
                DeliveryJob.status.in_(ACTIVE_DELIVERY_STATUSES),
            )
            .first()
        )

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        status: str | None = None,
        custom_order_id: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 1,
        per_page: int = 100,
    ) -> tuple[list[DeliveryJob], int]:
        query = DeliveryJob.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status.upper())
        if custom_order_id:
            query = query.filter_by(custom_order_id=custom_order_id)
        if from_date is not None:
            query = query.filter(DeliveryJob.scheduled_at >= from_date)
        if to_date is not None:
            query = query.filter(DeliveryJob.scheduled_at < to_date)
        total = query.with_entities(func.count(DeliveryJob.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 100), 1), 200)
        rows = (
            query.order_by(
                DeliveryJob.scheduled_at.is_(None),
                DeliveryJob.scheduled_at.asc(),
                DeliveryJob.created_at.desc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(DeliveryNumberCounter)
            .filter(DeliveryNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = DeliveryNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"DL-{sequence:05d}"

    @staticmethod
    def add(row: DeliveryJob) -> DeliveryJob:
        db.session.add(row)
        return row
