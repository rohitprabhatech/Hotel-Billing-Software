"""Category data access — tenant scoped."""

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.category import Category


class CategoryRepository:
    @staticmethod
    def get_by_id_and_tenant(category_id: str, tenant_id: str) -> Category | None:
        return (
            db.session.query(Category)
            .options(joinedload(Category.parent))
            .filter(Category.id == category_id, Category.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        active_only: bool = False,
        parent_id: str | None = None,
        include_all_parents: bool = True,
    ) -> list[Category]:
        query = (
            db.session.query(Category)
            .options(joinedload(Category.parent))
            .filter(Category.tenant_id == tenant_id)
        )
        if active_only:
            query = query.filter(Category.is_active.is_(True))
        if not include_all_parents and parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)
        elif not include_all_parents and parent_id is None:
            query = query.filter(Category.parent_id.is_(None))
        return query.order_by(Category.name.asc()).all()

    @staticmethod
    def find_by_tenant_parent_name(
        tenant_id: str, parent_id: str | None, name: str
    ) -> Category | None:
        query = db.session.query(Category).filter(
            Category.tenant_id == tenant_id,
            func.lower(Category.name) == name.lower().strip(),
        )
        if parent_id is None:
            query = query.filter(Category.parent_id.is_(None))
        else:
            query = query.filter(Category.parent_id == parent_id)
        return query.first()

    @staticmethod
    def count_children(category_id: str, tenant_id: str) -> int:
        return (
            db.session.query(Category)
            .filter(
                Category.tenant_id == tenant_id,
                Category.parent_id == category_id,
            )
            .count()
        )

    @staticmethod
    def count_items(category_id: str, tenant_id: str) -> int:
        from app.models.item import Item

        return (
            db.session.query(Item)
            .filter(Item.tenant_id == tenant_id, Item.category_id == category_id)
            .count()
        )

    @staticmethod
    def list_descendant_ids(category_id: str, tenant_id: str) -> set[str]:
        """Return all descendant category IDs for a tenant (not including itself)."""
        rows = (
            db.session.query(Category.id, Category.parent_id)
            .filter(Category.tenant_id == tenant_id)
            .all()
        )
        children_map: dict[str | None, list[str]] = {}
        for row_id, parent_id in rows:
            children_map.setdefault(parent_id, []).append(row_id)

        descendants: set[str] = set()
        stack = list(children_map.get(category_id, []))
        while stack:
            current = stack.pop()
            if current in descendants:
                continue
            descendants.add(current)
            stack.extend(children_map.get(current, []))
        return descendants

    @staticmethod
    def add(category: Category) -> Category:
        db.session.add(category)
        return category
