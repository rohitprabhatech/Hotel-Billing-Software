"""Recipe BOM business logic (BIZ-16)."""

from decimal import Decimal

from app.constants.permissions import PERM_RECIPES_READ, PERM_RECIPES_WRITE
from app.extensions import db
from app.models.recipe import Recipe, RecipeIngredient
from app.repositories.item_repository import ItemRepository
from app.repositories.recipe_repository import RecipeRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class RecipeService:
    @staticmethod
    def list_recipes(*, menu_item_id=None, q=None, page=1, per_page=50):
        require_permission(PERM_RECIPES_READ)
        ctx = require_request_context()
        rows, total = RecipeRepository.list_by_tenant(
            ctx.tenant_id,
            menu_item_id=menu_item_id,
            q=q,
            page=page,
            per_page=per_page,
        )
        return (
            [RecipeService.serialize(row, include_ingredients=False) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_recipe(recipe_id: str):
        require_permission(PERM_RECIPES_READ)
        ctx = require_request_context()
        recipe = RecipeRepository.get_by_id_and_tenant(recipe_id, ctx.tenant_id)
        if recipe is None:
            raise NotFoundError("Recipe not found")
        return RecipeService.serialize(recipe, include_ingredients=True)

    @staticmethod
    def get_by_menu_item(menu_item_id: str):
        require_permission(PERM_RECIPES_READ)
        ctx = require_request_context()
        recipe = RecipeRepository.get_by_menu_item(ctx.tenant_id, menu_item_id)
        if recipe is None:
            raise NotFoundError("Recipe not found for this menu item")
        return RecipeService.serialize(recipe, include_ingredients=True)

    @staticmethod
    def create_recipe(*, menu_item_id: str, name=None, yield_quantity=1, ingredients: list[dict]):
        require_permission(PERM_RECIPES_WRITE)
        ctx = require_request_context()
        menu_item = ItemRepository.get_by_id_and_tenant(menu_item_id.strip(), ctx.tenant_id)
        if menu_item is None or not menu_item.is_active:
            raise ValidationError("Menu item not found or inactive")
        if not menu_item.is_menu:
            from app.repositories.tenant_repository import TenantRepository
            from app.services.module_service import ModuleService
            from app.constants.business_types import coerce_business_type

            tenant = TenantRepository.get_by_id(ctx.tenant_id)
            # Bakery production reuses recipes for finished goods that are not F&B menu rows.
            if tenant and ModuleService.is_enabled_for_tenant(tenant, "production"):
                pass
            elif tenant and coerce_business_type(tenant.business_type) in {
                "hotel_restaurant",
                "cafe_tea",
            }:
                # Hotel/cafe dishes are often created without is_menu — promote when linking a recipe.
                menu_item.is_menu = True
            else:
                raise ValidationError("Recipes can only be linked to menu items")

        existing = RecipeRepository.get_by_menu_item(ctx.tenant_id, menu_item.id)
        if existing is not None:
            raise ConflictError("A recipe already exists for this menu item")

        parsed_yield = qty(yield_quantity)
        if parsed_yield <= 0:
            raise ValidationError("Yield quantity must be greater than zero")

        recipe = Recipe(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            menu_item_id=menu_item.id,
            name=(name or "").strip() or menu_item.name,
            yield_quantity=parsed_yield,
            is_active=True,
            created_by=ctx.user_id,
        )
        RecipeService._replace_ingredients(recipe, ingredients, ctx.tenant_id)
        RecipeRepository.add(recipe)

        serialized = RecipeService.serialize(recipe, include_ingredients=True)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_RECIPE",
            entity_type="RECIPE",
            entity_id=recipe.id,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def update_recipe(recipe_id: str, **fields):
        require_permission(PERM_RECIPES_WRITE)
        ctx = require_request_context()
        recipe = RecipeRepository.get_by_id_and_tenant(recipe_id, ctx.tenant_id)
        if recipe is None:
            raise NotFoundError("Recipe not found")
        old = RecipeService.serialize(recipe, include_ingredients=True)

        if fields.get("name_provided"):
            recipe.name = (fields.get("name") or "").strip() or recipe.menu_item.name
        if fields.get("yield_quantity_provided"):
            parsed_yield = qty(fields.get("yield_quantity"))
            if parsed_yield <= 0:
                raise ValidationError("Yield quantity must be greater than zero")
            recipe.yield_quantity = parsed_yield
        if fields.get("is_active_provided"):
            recipe.is_active = bool(fields.get("is_active"))

        if fields.get("ingredients_provided"):
            RecipeService._replace_ingredients(recipe, fields.get("ingredients") or [], ctx.tenant_id)

        serialized = RecipeService.serialize(recipe, include_ingredients=True)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_RECIPE",
            entity_type="RECIPE",
            entity_id=recipe.id,
            old_data=old,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def delete_recipe(recipe_id: str):
        require_permission(PERM_RECIPES_WRITE)
        ctx = require_request_context()
        recipe = RecipeRepository.get_by_id_and_tenant(recipe_id, ctx.tenant_id)
        if recipe is None:
            raise NotFoundError("Recipe not found")
        old = RecipeService.serialize(recipe, include_ingredients=True)
        RecipeRepository.delete(recipe)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_RECIPE",
            entity_type="RECIPE",
            entity_id=recipe.id,
            old_data=old,
        )
        db.session.commit()
        return {"id": recipe_id, "deleted": True}

    @staticmethod
    def _replace_ingredients(recipe: Recipe, ingredients: list[dict], tenant_id: str):
        recipe.ingredients.clear()
        seen: set[str] = set()
        for index, row in enumerate(ingredients):
            ingredient_id = (row.get("ingredient_item_id") or "").strip()
            if not ingredient_id:
                raise ValidationError("ingredient_item_id is required for each line")
            if ingredient_id in seen:
                raise ValidationError("Duplicate ingredient in recipe")
            if ingredient_id == recipe.menu_item_id:
                raise ValidationError("Menu item cannot be its own ingredient")
            seen.add(ingredient_id)

            item = ItemRepository.get_by_id_and_tenant(ingredient_id, tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Ingredient not found or inactive: {ingredient_id}")
            if item.is_menu:
                raise ValidationError("Ingredients must be non-menu stock items")

            parsed_qty = qty(row.get("quantity"))
            if parsed_qty <= 0:
                raise ValidationError("Ingredient quantity must be greater than zero")

            recipe.ingredients.append(
                RecipeIngredient(
                    id=new_uuid(),
                    tenant_id=tenant_id,
                    recipe_id=recipe.id,
                    ingredient_item_id=item.id,
                    ingredient_name=item.name,
                    quantity=parsed_qty,
                    uom=item.uom,
                    sort_order=index,
                )
            )

    @staticmethod
    def serialize(recipe: Recipe, *, include_ingredients: bool = True):
        data = {
            "id": recipe.id,
            "menu_item_id": recipe.menu_item_id,
            "menu_item_name": recipe.menu_item.name if recipe.menu_item else None,
            "menu_item_tracks_batches": bool(
                getattr(recipe.menu_item, "tracks_batches", False) if recipe.menu_item else False
            ),
            "name": recipe.name,
            "yield_quantity": float(recipe.yield_quantity),
            "is_active": recipe.is_active,
            "ingredient_count": len(recipe.ingredients or []),
            "created_by": recipe.created_by,
            "created_by_name": recipe.creator.name if recipe.creator else None,
            "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
            "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None,
        }
        if include_ingredients:
            data["ingredients"] = [
                {
                    "id": line.id,
                    "ingredient_item_id": line.ingredient_item_id,
                    "ingredient_name": line.ingredient_name,
                    "quantity": float(line.quantity),
                    "uom": line.uom,
                    "sort_order": line.sort_order,
                }
                for line in recipe.ingredients
            ]
        return data
