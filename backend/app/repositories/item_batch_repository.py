"""Item batch persistence (BIZ-22)."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import case, or_

from app.extensions import db
from app.models.item_batch import ItemBatch


class ItemBatchRepository:
    @staticmethod
    def get_by_id(tenant_id: str, batch_id: str) -> ItemBatch | None:
        return ItemBatch.query.filter_by(tenant_id=tenant_id, id=batch_id).first()

    @staticmethod
    def list_by_item(tenant_id: str, item_id: str, *, active_only: bool = True) -> list[ItemBatch]:
        query = ItemBatch.query.filter_by(tenant_id=tenant_id, item_id=item_id)
        if active_only:
            query = query.filter(ItemBatch.is_active.is_(True), ItemBatch.quantity > 0)
        return query.order_by(
            case((ItemBatch.expiry_date.is_(None), 1), else_=0),
            ItemBatch.expiry_date.asc(),
            ItemBatch.created_at.asc(),
        ).all()

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        item_id: str | None = None,
        status: str | None = None,
        within_days: int | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[ItemBatch], int]:
        today = date.today()
        query = ItemBatch.query.filter_by(tenant_id=tenant_id, is_active=True)
        query = query.filter(ItemBatch.quantity > 0)
        if item_id:
            query = query.filter_by(item_id=item_id)

        status_key = (status or "").strip().lower()
        if status_key == "expired":
            query = query.filter(
                ItemBatch.expiry_date.isnot(None),
                ItemBatch.expiry_date < today,
            )
        elif status_key == "expiring":
            days = max(int(within_days or 7), 0)
            end = today + timedelta(days=days)
            query = query.filter(
                ItemBatch.expiry_date.isnot(None),
                ItemBatch.expiry_date >= today,
                ItemBatch.expiry_date <= end,
            )
        elif status_key == "ok":
            days = max(int(within_days or 7), 0)
            end = today + timedelta(days=days)
            query = query.filter(
                or_(
                    ItemBatch.expiry_date.is_(None),
                    ItemBatch.expiry_date > end,
                )
            )

        total = query.count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 200)
        rows = (
            query.order_by(
                case((ItemBatch.expiry_date.is_(None), 1), else_=0),
                ItemBatch.expiry_date.asc(),
                ItemBatch.created_at.asc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def sellable_batches(tenant_id: str, item_id: str, *, as_of: date | None = None) -> list[ItemBatch]:
        """FEFO: non-expired batches with qty > 0, earliest expiry first."""
        today = as_of or date.today()
        return (
            ItemBatch.query.filter_by(tenant_id=tenant_id, item_id=item_id, is_active=True)
            .filter(ItemBatch.quantity > 0)
            .filter(
                or_(
                    ItemBatch.expiry_date.is_(None),
                    ItemBatch.expiry_date >= today,
                )
            )
            .order_by(
                case((ItemBatch.expiry_date.is_(None), 1), else_=0),
                ItemBatch.expiry_date.asc(),
                ItemBatch.created_at.asc(),
            )
            .all()
        )

    @staticmethod
    def sellable_quantity(tenant_id: str, item_id: str, *, as_of: date | None = None) -> Decimal:
        total = Decimal("0")
        for row in ItemBatchRepository.sellable_batches(tenant_id, item_id, as_of=as_of):
            total += Decimal(row.quantity)
        return total

    @staticmethod
    def writeoff_batches(tenant_id: str, item_id: str) -> list[ItemBatch]:
        """FEFO including expired — for wastage / write-off of perishable FG."""
        return (
            ItemBatch.query.filter_by(tenant_id=tenant_id, item_id=item_id, is_active=True)
            .filter(ItemBatch.quantity > 0)
            .order_by(
                case((ItemBatch.expiry_date.is_(None), 1), else_=0),
                ItemBatch.expiry_date.asc(),
                ItemBatch.created_at.asc(),
            )
            .all()
        )

    @staticmethod
    def add(batch: ItemBatch) -> ItemBatch:
        db.session.add(batch)
        return batch

    @staticmethod
    def find_by_code(tenant_id: str, item_id: str, batch_code: str) -> ItemBatch | None:
        return ItemBatch.query.filter_by(
            tenant_id=tenant_id,
            item_id=item_id,
            batch_code=batch_code,
        ).first()
