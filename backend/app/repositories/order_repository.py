"""Order data access — tenant scoped."""

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload, noload

from app.constants.orders import ORDER_STATUS_OPEN
from app.extensions import db
from app.models.order import Order, OrderItem, OrderNumberCounter


class OrderRepository:
    @staticmethod
    def get_by_id_and_tenant(order_id: str, tenant_id: str) -> Order | None:
        return (
            db.session.query(Order)
            .options(
                joinedload(Order.items),
                joinedload(Order.dining_table),
                joinedload(Order.customer),
                joinedload(Order.creator),
            )
            .filter(Order.id == order_id, Order.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def get_open_by_table(tenant_id: str, dining_table_id: str) -> Order | None:
        return (
            db.session.query(Order)
            .filter(
                Order.tenant_id == tenant_id,
                Order.dining_table_id == dining_table_id,
                Order.status == ORDER_STATUS_OPEN,
            )
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        status: str | None = None,
        channel: str | None = None,
        dining_table_id: str | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Order], int]:
        query = db.session.query(Order).filter(Order.tenant_id == tenant_id)
        if status:
            query = query.filter(Order.status == status)
        if channel:
            query = query.filter(Order.channel == channel)
        if dining_table_id:
            query = query.filter(Order.dining_table_id == dining_table_id)
        if q:
            term = q.strip()
            like = f"%{term}%"
            query = query.filter(
                or_(
                    Order.order_number.ilike(like),
                    Order.customer_name.ilike(like),
                    Order.notes.ilike(like),
                )
            )
        total = query.with_entities(func.count(Order.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.options(
                noload(Order.items),
                joinedload(Order.dining_table),
                joinedload(Order.creator),
            )
            .order_by(Order.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_order_number(tenant_id: str, prefix: str | None = "ORD-") -> tuple[int, str]:
        counter = (
            db.session.query(OrderNumberCounter)
            .filter(OrderNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = OrderNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()

        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        label = f"{prefix or ''}{sequence}"
        return sequence, label

    @staticmethod
    def count_items_by_order_ids(tenant_id: str, order_ids: list[str]) -> dict[str, int]:
        if not order_ids:
            return {}
        rows = (
            db.session.query(OrderItem.order_id, func.count(OrderItem.id))
            .filter(OrderItem.tenant_id == tenant_id, OrderItem.order_id.in_(order_ids))
            .group_by(OrderItem.order_id)
            .all()
        )
        return {order_id: int(count) for order_id, count in rows}

    @staticmethod
    def add(order: Order) -> Order:
        db.session.add(order)
        return order

    @staticmethod
    def get_item_line(order_id: str, line_id: str, tenant_id: str) -> OrderItem | None:
        return (
            db.session.query(OrderItem)
            .filter(
                OrderItem.id == line_id,
                OrderItem.order_id == order_id,
                OrderItem.tenant_id == tenant_id,
            )
            .first()
        )
