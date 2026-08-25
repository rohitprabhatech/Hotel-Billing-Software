"""Item variant persistence (BIZ-25)."""

from sqlalchemy import func

from app.extensions import db
from app.models.item_variant import ItemVariant


class ItemVariantRepository:
    @staticmethod
    def list_by_item(tenant_id: str, item_id: str, *, active_only: bool = False) -> list[ItemVariant]:
        query = ItemVariant.query.filter_by(tenant_id=tenant_id, item_id=item_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(ItemVariant.size.asc(), ItemVariant.color.asc()).all()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, item_id: str | None = None, page: int = 1, per_page: int = 50
    ) -> tuple[list[ItemVariant], int]:
        query = ItemVariant.query.filter_by(tenant_id=tenant_id, is_active=True)
        if item_id:
            query = query.filter_by(item_id=item_id)
        total = query.with_entities(func.count(ItemVariant.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(ItemVariant.item_id.asc(), ItemVariant.size.asc(), ItemVariant.color.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def list_active_for_items(tenant_id: str, item_ids: list[str]) -> dict[str, list[ItemVariant]]:
        if not item_ids:
            return {}
        rows = (
            ItemVariant.query.filter(
                ItemVariant.tenant_id == tenant_id,
                ItemVariant.item_id.in_(item_ids),
                ItemVariant.is_active.is_(True),
            )
            .order_by(ItemVariant.size.asc(), ItemVariant.color.asc())
            .all()
        )
        grouped: dict[str, list[ItemVariant]] = {item_id: [] for item_id in item_ids}
        for row in rows:
            grouped.setdefault(row.item_id, []).append(row)
        return grouped

    @staticmethod
    def get_by_id(tenant_id: str, variant_id: str) -> ItemVariant | None:
        return ItemVariant.query.filter_by(tenant_id=tenant_id, id=variant_id).first()

    @staticmethod
    def lock_by_id(tenant_id: str, variant_id: str) -> ItemVariant | None:
        return (
            db.session.query(ItemVariant)
            .filter(ItemVariant.tenant_id == tenant_id, ItemVariant.id == variant_id)
            .with_for_update()
            .first()
        )

    @staticmethod
    def find_size_color(tenant_id: str, item_id: str, size: str, color: str) -> ItemVariant | None:
        return ItemVariant.query.filter(
            ItemVariant.tenant_id == tenant_id,
            ItemVariant.item_id == item_id,
            func.lower(ItemVariant.size) == size.lower().strip(),
            func.lower(ItemVariant.color) == color.lower().strip(),
        ).first()

    @staticmethod
    def find_by_barcode(tenant_id: str, barcode: str) -> ItemVariant | None:
        cleaned = (barcode or "").strip()
        if not cleaned:
            return None
        return ItemVariant.query.filter(
            ItemVariant.tenant_id == tenant_id,
            func.lower(ItemVariant.barcode) == cleaned.lower(),
        ).first()

    @staticmethod
    def find_by_sku(tenant_id: str, sku: str) -> ItemVariant | None:
        cleaned = (sku or "").strip()
        if not cleaned:
            return None
        return ItemVariant.query.filter(
            ItemVariant.tenant_id == tenant_id,
            func.lower(ItemVariant.sku) == cleaned.lower(),
        ).first()

    @staticmethod
    def count_for_item(tenant_id: str, item_id: str) -> int:
        return int(
            ItemVariant.query.filter_by(tenant_id=tenant_id, item_id=item_id).with_entities(
                func.count(ItemVariant.id)
            ).scalar()
            or 0
        )

    @staticmethod
    def add(variant: ItemVariant) -> ItemVariant:
        db.session.add(variant)
        return variant

    @staticmethod
    def delete(variant: ItemVariant) -> None:
        db.session.delete(variant)

    @staticmethod
    def stock_sum(tenant_id: str, item_id: str):
        return (
            db.session.query(func.coalesce(func.sum(ItemVariant.stock_quantity), 0))
            .filter(
                ItemVariant.tenant_id == tenant_id,
                ItemVariant.item_id == item_id,
                ItemVariant.is_active.is_(True),
            )
            .scalar()
        )
