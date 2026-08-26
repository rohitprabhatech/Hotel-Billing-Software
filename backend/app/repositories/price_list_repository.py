"""Price list persistence (BIZ-51)."""

from decimal import Decimal

from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models.price_list import (
    LIST_TYPE_WHOLESALE,
    CustomerPriceList,
    PriceList,
    PriceListItem,
)


class PriceListRepository:
    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        list_type=None,
        active_only=False,
        page=1,
        per_page=100,
    ):
        query = PriceList.query.filter_by(tenant_id=tenant_id)
        if list_type:
            query = query.filter_by(list_type=(list_type or "").strip().upper())
        if active_only:
            query = query.filter_by(is_active=True)
        total = query.count()
        rows = (
            query.order_by(PriceList.is_default.desc(), PriceList.name.asc())
            .offset((max(int(page or 1), 1) - 1) * min(max(int(per_page or 100), 1), 200))
            .limit(min(max(int(per_page or 100), 1), 200))
            .all()
        )
        return rows, total

    @staticmethod
    def get_by_id(tenant_id: str, price_list_id: str) -> PriceList | None:
        return (
            PriceList.query.options(
                selectinload(PriceList.items).selectinload(PriceListItem.item)
            )
            .filter_by(tenant_id=tenant_id, id=price_list_id)
            .first()
        )

    @staticmethod
    def get_default(tenant_id: str, list_type: str = LIST_TYPE_WHOLESALE) -> PriceList | None:
        return (
            PriceList.query.filter_by(
                tenant_id=tenant_id,
                list_type=(list_type or LIST_TYPE_WHOLESALE).upper(),
                is_default=True,
                is_active=True,
            )
            .order_by(PriceList.updated_at.desc())
            .first()
        )

    @staticmethod
    def add(row) -> None:
        db.session.add(row)

    @staticmethod
    def delete(row) -> None:
        db.session.delete(row)

    @staticmethod
    def clear_default_for_type(tenant_id: str, list_type: str, *, except_id: str | None = None):
        query = PriceList.query.filter_by(
            tenant_id=tenant_id,
            list_type=(list_type or LIST_TYPE_WHOLESALE).upper(),
            is_default=True,
        )
        if except_id:
            query = query.filter(PriceList.id != except_id)
        for row in query.all():
            row.is_default = False

    @staticmethod
    def list_items(tenant_id: str, price_list_id: str, *, active_only=False) -> list[PriceListItem]:
        query = PriceListItem.query.filter_by(tenant_id=tenant_id, price_list_id=price_list_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(PriceListItem.item_id.asc()).all()

    @staticmethod
    def items_map(
        tenant_id: str,
        price_list_id: str,
        item_ids: list[str],
        *,
        active_only=True,
    ) -> dict[str, Decimal]:
        if not item_ids:
            return {}
        query = PriceListItem.query.filter(
            PriceListItem.tenant_id == tenant_id,
            PriceListItem.price_list_id == price_list_id,
            PriceListItem.item_id.in_(item_ids),
        )
        if active_only:
            query = query.filter_by(is_active=True)
        return {row.item_id: Decimal(row.unit_price) for row in query.all()}

    @staticmethod
    def items_map_for_lists(
        tenant_id: str,
        price_list_ids: list[str],
        item_ids: list[str],
        *,
        active_only=True,
    ) -> dict[str, dict[str, Decimal]]:
        if not price_list_ids or not item_ids:
            return {}
        query = PriceListItem.query.filter(
            PriceListItem.tenant_id == tenant_id,
            PriceListItem.price_list_id.in_(price_list_ids),
            PriceListItem.item_id.in_(item_ids),
        )
        if active_only:
            query = query.filter_by(is_active=True)
        grouped: dict[str, dict[str, Decimal]] = {}
        for row in query.all():
            grouped.setdefault(row.price_list_id, {})[row.item_id] = Decimal(row.unit_price)
        return grouped

    @staticmethod
    def delete_items_for_list(tenant_id: str, price_list_id: str) -> int:
        rows = PriceListItem.query.filter_by(tenant_id=tenant_id, price_list_id=price_list_id).all()
        for row in rows:
            db.session.delete(row)
        return len(rows)

    @staticmethod
    def get_assignment(tenant_id: str, customer_id: str) -> CustomerPriceList | None:
        return CustomerPriceList.query.filter_by(
            tenant_id=tenant_id, customer_id=customer_id
        ).first()

    @staticmethod
    def list_assignments(tenant_id: str, *, price_list_id=None) -> list[CustomerPriceList]:
        query = CustomerPriceList.query.filter_by(tenant_id=tenant_id)
        if price_list_id:
            query = query.filter_by(price_list_id=price_list_id)
        return query.order_by(CustomerPriceList.assigned_at.desc()).all()

    @staticmethod
    def delete_assignment(row: CustomerPriceList) -> None:
        db.session.delete(row)
