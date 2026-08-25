"""Item accessory repository (BIZ-30)."""

from app.extensions import db
from app.models.item_accessory import ItemAccessory


class ItemAccessoryRepository:
    @staticmethod
    def list_for_item(tenant_id: str, item_id: str) -> list[ItemAccessory]:
        return (
            db.session.query(ItemAccessory)
            .filter(ItemAccessory.tenant_id == tenant_id, ItemAccessory.item_id == item_id)
            .order_by(ItemAccessory.sort_order.asc(), ItemAccessory.created_at.asc())
            .all()
        )

    @staticmethod
    def delete_for_item(tenant_id: str, item_id: str) -> None:
        db.session.query(ItemAccessory).filter(
            ItemAccessory.tenant_id == tenant_id,
            ItemAccessory.item_id == item_id,
        ).delete(synchronize_session=False)

    @staticmethod
    def add(link: ItemAccessory) -> None:
        db.session.add(link)
