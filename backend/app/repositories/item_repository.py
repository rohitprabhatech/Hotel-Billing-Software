"""Item data access — tenant scoped."""

from sqlalchemy import func

from app.extensions import db
from app.models.item import Item


class ItemRepository:
    @staticmethod
    def get_by_id_and_tenant(item_id: str, tenant_id: str) -> Item | None:
        return (
            db.session.query(Item)
            .filter(Item.id == item_id, Item.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def find_by_tenant_and_name(tenant_id: str, name: str) -> Item | None:
        return (
            db.session.query(Item)
            .filter(
                Item.tenant_id == tenant_id,
                func.lower(Item.name) == name.lower().strip(),
            )
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        q: str | None = None,
        category_id: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Item], int]:
        query = db.session.query(Item).filter(Item.tenant_id == tenant_id)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(Item.name.ilike(like))
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if is_active is not None:
            query = query.filter(Item.is_active.is_(is_active))

        total = query.count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        items = (
            query.order_by(Item.name.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return items, total

    @staticmethod
    def add(item: Item) -> Item:
        db.session.add(item)
        return item
