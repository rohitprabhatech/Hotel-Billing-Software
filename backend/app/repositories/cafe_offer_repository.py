"""Cafe offer data access."""

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.cafe_offer import Combo, ComboItem, ItemAddon, ItemAddonGroup


class AddonRepository:
    @staticmethod
    def list_groups_for_menu_items(tenant_id: str, menu_item_ids: list[str]) -> list[ItemAddonGroup]:
        if not menu_item_ids:
            return []
        return (
            db.session.query(ItemAddonGroup)
            .options(joinedload(ItemAddonGroup.addons))
            .filter(
                ItemAddonGroup.tenant_id == tenant_id,
                ItemAddonGroup.menu_item_id.in_(menu_item_ids),
                ItemAddonGroup.is_active.is_(True),
            )
            .order_by(ItemAddonGroup.sort_order.asc())
            .all()
        )

    @staticmethod
    def list_groups_by_tenant(tenant_id: str) -> list[ItemAddonGroup]:
        return (
            db.session.query(ItemAddonGroup)
            .options(joinedload(ItemAddonGroup.addons), joinedload(ItemAddonGroup.menu_item))
            .filter(ItemAddonGroup.tenant_id == tenant_id)
            .order_by(ItemAddonGroup.menu_item_id.asc(), ItemAddonGroup.sort_order.asc())
            .all()
        )

    @staticmethod
    def get_group_by_id(tenant_id: str, group_id: str) -> ItemAddonGroup | None:
        return (
            db.session.query(ItemAddonGroup)
            .options(joinedload(ItemAddonGroup.addons), joinedload(ItemAddonGroup.menu_item))
            .filter(ItemAddonGroup.id == group_id, ItemAddonGroup.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def get_addons_by_ids(tenant_id: str, addon_ids: list[str]) -> list[ItemAddon]:
        if not addon_ids:
            return []
        return (
            db.session.query(ItemAddon)
            .options(joinedload(ItemAddon.group))
            .filter(ItemAddon.tenant_id == tenant_id, ItemAddon.id.in_(addon_ids), ItemAddon.is_active.is_(True))
            .all()
        )

    @staticmethod
    def add_group(group: ItemAddonGroup) -> ItemAddonGroup:
        db.session.add(group)
        return group

    @staticmethod
    def delete_group(group: ItemAddonGroup) -> None:
        db.session.delete(group)


class ComboRepository:
    @staticmethod
    def list_by_tenant(tenant_id: str, *, popular_only=False) -> list[Combo]:
        query = db.session.query(Combo).filter(Combo.tenant_id == tenant_id, Combo.is_active.is_(True))
        if popular_only:
            query = query.filter(Combo.is_popular.is_(True))
        return (
            query.options(joinedload(Combo.items).joinedload(ComboItem.item))
            .order_by(Combo.is_popular.desc(), Combo.name.asc())
            .all()
        )

    @staticmethod
    def get_by_id(tenant_id: str, combo_id: str) -> Combo | None:
        return (
            db.session.query(Combo)
            .options(joinedload(Combo.items).joinedload(ComboItem.item))
            .filter(Combo.id == combo_id, Combo.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def add(combo: Combo) -> Combo:
        db.session.add(combo)
        return combo

    @staticmethod
    def delete(combo: Combo) -> None:
        db.session.delete(combo)
