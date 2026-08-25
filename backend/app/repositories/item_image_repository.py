"""Item image persistence (BIZ-26)."""

from sqlalchemy import func

from app.extensions import db
from app.models.item_image import ItemImage


class ItemImageRepository:
    @staticmethod
    def list_by_item(tenant_id: str, item_id: str) -> list[ItemImage]:
        return (
            ItemImage.query.filter_by(tenant_id=tenant_id, item_id=item_id)
            .order_by(ItemImage.is_primary.desc(), ItemImage.sort_order.asc(), ItemImage.created_at.asc())
            .all()
        )

    @staticmethod
    def get_by_id(tenant_id: str, image_id: str) -> ItemImage | None:
        return ItemImage.query.filter_by(tenant_id=tenant_id, id=image_id).first()

    @staticmethod
    def count_for_item(tenant_id: str, item_id: str) -> int:
        return int(
            ItemImage.query.filter_by(tenant_id=tenant_id, item_id=item_id)
            .with_entities(func.count(ItemImage.id))
            .scalar()
            or 0
        )

    @staticmethod
    def next_sort_order(tenant_id: str, item_id: str) -> int:
        current = (
            db.session.query(func.coalesce(func.max(ItemImage.sort_order), -1))
            .filter(ItemImage.tenant_id == tenant_id, ItemImage.item_id == item_id)
            .scalar()
        )
        return int(current) + 1

    @staticmethod
    def primary_by_item_ids(tenant_id: str, item_ids: list[str]) -> dict[str, ItemImage]:
        if not item_ids:
            return {}
        rows = (
            ItemImage.query.filter(
                ItemImage.tenant_id == tenant_id,
                ItemImage.item_id.in_(item_ids),
                ItemImage.is_primary.is_(True),
            ).all()
        )
        return {row.item_id: row for row in rows}

    @staticmethod
    def clear_primary(tenant_id: str, item_id: str) -> None:
        ItemImage.query.filter_by(tenant_id=tenant_id, item_id=item_id, is_primary=True).update(
            {"is_primary": False}
        )

    @staticmethod
    def add(image: ItemImage) -> ItemImage:
        db.session.add(image)
        return image

    @staticmethod
    def delete(image: ItemImage) -> None:
        db.session.delete(image)
