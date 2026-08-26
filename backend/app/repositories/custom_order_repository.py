"""Custom product order data access (BIZ-42)."""

from datetime import datetime

from sqlalchemy import case, func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.custom_order import (
    CustomOrderNumberCounter,
    CustomOrderPayment,
    CustomProductOrder,
)


class CustomOrderRepository:
    @staticmethod
    def get_by_id(tenant_id: str, order_id: str) -> CustomProductOrder | None:
        return (
            db.session.query(CustomProductOrder)
            .options(
                joinedload(CustomProductOrder.payments),
                joinedload(CustomProductOrder.customer),
                joinedload(CustomProductOrder.creator),
            )
            .filter(
                CustomProductOrder.id == order_id,
                CustomProductOrder.tenant_id == tenant_id,
            )
            .first()
        )

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        order_type: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 100,
    ) -> tuple[list[CustomProductOrder], int]:
        query = db.session.query(CustomProductOrder).filter(
            CustomProductOrder.tenant_id == tenant_id
        )
        if order_type:
            query = query.filter(CustomProductOrder.order_type == order_type)
        if status:
            query = query.filter(CustomProductOrder.status == status)
        total = query.with_entities(func.count(CustomProductOrder.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 100), 1), 200)
        rows = (
            query.options(joinedload(CustomProductOrder.payments))
            .order_by(
                case((CustomProductOrder.delivery_at.is_(None), 1), else_=0),
                CustomProductOrder.delivery_at.asc(),
                CustomProductOrder.created_at.desc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(CustomOrderNumberCounter)
            .filter(CustomOrderNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = CustomOrderNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"CO-{sequence:05d}"

    @staticmethod
    def add(order: CustomProductOrder) -> CustomProductOrder:
        db.session.add(order)
        return order

    @staticmethod
    def add_payment(payment: CustomOrderPayment) -> CustomOrderPayment:
        db.session.add(payment)
        return payment

    @staticmethod
    def upcoming_deliveries(
        tenant_id: str, *, before: datetime, after: datetime | None = None
    ) -> list[CustomProductOrder]:
        query = CustomProductOrder.query.filter(
            CustomProductOrder.tenant_id == tenant_id,
            CustomProductOrder.delivery_at.isnot(None),
            CustomProductOrder.delivery_at <= before,
            CustomProductOrder.status.notin_(["DELIVERED", "CANCELLED"]),
        )
        if after is not None:
            query = query.filter(CustomProductOrder.delivery_at >= after)
        return query.order_by(CustomProductOrder.delivery_at.asc()).limit(100).all()
