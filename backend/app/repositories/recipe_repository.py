"""Recipe data access — tenant scoped."""

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.recipe import Recipe, RecipeIngredient


class RecipeRepository:
    @staticmethod
    def get_by_id_and_tenant(recipe_id: str, tenant_id: str) -> Recipe | None:
        return (
            db.session.query(Recipe)
            .options(
                joinedload(Recipe.ingredients),
                joinedload(Recipe.menu_item),
                joinedload(Recipe.creator),
            )
            .filter(Recipe.id == recipe_id, Recipe.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def get_by_menu_item(tenant_id: str, menu_item_id: str) -> Recipe | None:
        return (
            db.session.query(Recipe)
            .options(joinedload(Recipe.ingredients))
            .filter(
                Recipe.tenant_id == tenant_id,
                Recipe.menu_item_id == menu_item_id,
                Recipe.is_active.is_(True),
            )
            .first()
        )

    @staticmethod
    def map_active_by_menu_item_ids(tenant_id: str, menu_item_ids: list[str]) -> dict[str, Recipe]:
        if not menu_item_ids:
            return {}
        rows = (
            db.session.query(Recipe)
            .options(joinedload(Recipe.ingredients))
            .filter(
                Recipe.tenant_id == tenant_id,
                Recipe.menu_item_id.in_(menu_item_ids),
                Recipe.is_active.is_(True),
            )
            .all()
        )
        return {row.menu_item_id: row for row in rows}

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        menu_item_id: str | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Recipe], int]:
        from sqlalchemy import func, or_

        query = db.session.query(Recipe).filter(Recipe.tenant_id == tenant_id)
        if menu_item_id:
            query = query.filter(Recipe.menu_item_id == menu_item_id)
        if q:
            from app.models.item import Item

            term = q.strip()
            like = f"%{term}%"
            query = query.join(Item, Recipe.menu_item_id == Item.id).filter(
                or_(Recipe.name.ilike(like), Item.name.ilike(like))
            )
        total = query.with_entities(func.count(Recipe.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.options(joinedload(Recipe.menu_item), joinedload(Recipe.ingredients))
            .order_by(Recipe.updated_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def add(recipe: Recipe) -> Recipe:
        db.session.add(recipe)
        return recipe

    @staticmethod
    def delete(recipe: Recipe) -> None:
        db.session.delete(recipe)
