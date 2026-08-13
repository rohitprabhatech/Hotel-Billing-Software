"""Category data access — tenant scoped."""

from sqlalchemy import func

from app.extensions import db
from app.models.category import Category


class CategoryRepository:
    @staticmethod
    def get_by_id_and_tenant(category_id: str, tenant_id: str) -> Category | None:
        return (
            db.session.query(Category)
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
        query = db.session.query(Category).filter(Category.tenant_id == tenant_id)
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
    def add(category: Category) -> Category:
        db.session.add(category)
        return category