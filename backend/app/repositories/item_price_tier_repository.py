"""Item price tier persistence (BIZ-21)."""

from decimal import Decimal

from app.extensions import db
from app.models.item_price_tier import ItemPriceTier


class ItemPriceTierRepository:
    @staticmethod
    def list_by_item(tenant_id: str, item_id: str, *, active_only: bool = False) -> list[ItemPriceTier]:
        query = ItemPriceTier.query.filter_by(tenant_id=tenant_id, item_id=item_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(ItemPriceTier.min_quantity.asc()).all()

    @staticmethod
    def list_by_item_ids(
        tenant_id: str, item_ids: list[str], *, active_only: bool = True
    ) -> dict[str, list[ItemPriceTier]]:
        if not item_ids:
            return {}
        query = ItemPriceTier.query.filter(
            ItemPriceTier.tenant_id == tenant_id,
            ItemPriceTier.item_id.in_(item_ids),
        )
        if active_only:
            query = query.filter_by(is_active=True)
        rows = query.order_by(ItemPriceTier.min_quantity.asc()).all()
        grouped: dict[str, list[ItemPriceTier]] = {item_id: [] for item_id in item_ids}
        for row in rows:
            grouped.setdefault(row.item_id, []).append(row)
        return grouped

    @staticmethod
    def get_by_id(tenant_id: str, tier_id: str) -> ItemPriceTier | None:
        return ItemPriceTier.query.filter_by(tenant_id=tenant_id, id=tier_id).first()

    @staticmethod
    def add(tier: ItemPriceTier) -> ItemPriceTier:
        db.session.add(tier)
        return tier

    @staticmethod
    def delete(tier: ItemPriceTier) -> None:
        db.session.delete(tier)

    @staticmethod
    def delete_for_item(tenant_id: str, item_id: str) -> int:
        rows = ItemPriceTier.query.filter_by(tenant_id=tenant_id, item_id=item_id).all()
        count = len(rows)
        for row in rows:
            db.session.delete(row)
        return count

    @staticmethod
    def resolve_unit_price(
        tiers: list[ItemPriceTier],
        quantity: Decimal,
        base_price: Decimal,
    ) -> Decimal:
        """Pick the best matching tier: highest min_quantity that is <= quantity."""
        matched = None
        for tier in tiers:
            if not tier.is_active:
                continue
            if Decimal(tier.min_quantity) <= quantity:
                matched = tier
            else:
                break
        if matched is None:
            return Decimal(base_price)
        return Decimal(matched.unit_price)
