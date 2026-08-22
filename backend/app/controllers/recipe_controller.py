"""Recipe HTTP controller (BIZ-16)."""

from flask import request

from app.schemas.recipe_schemas import create_recipe_schema, update_recipe_schema
from app.services.recipe_service import RecipeService
from app.utils.responses import success_response


def list_recipes():
    menu_item_id = request.args.get("menu_item_id")
    q = request.args.get("q")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = RecipeService.list_recipes(
        menu_item_id=menu_item_id,
        q=q,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_recipe(recipe_id: str):
    return success_response(data=RecipeService.get_recipe(recipe_id))


def get_recipe_by_menu_item(menu_item_id: str):
    return success_response(data=RecipeService.get_by_menu_item(menu_item_id))


def create_recipe():
    payload = create_recipe_schema.load(request.get_json() or {})
    data = RecipeService.create_recipe(
        menu_item_id=payload["menu_item_id"],
        name=payload.get("name"),
        yield_quantity=payload.get("yield_quantity", 1),
        ingredients=payload.get("ingredients") or [],
    )
    return success_response(data=data, status_code=201)


def update_recipe(recipe_id: str):
    raw = request.get_json() or {}
    update_recipe_schema.load(raw)
    data = RecipeService.update_recipe(
        recipe_id,
        name=raw.get("name") if "name" in raw else None,
        yield_quantity=raw.get("yield_quantity") if "yield_quantity" in raw else None,
        is_active=raw.get("is_active") if "is_active" in raw else None,
        ingredients=raw.get("ingredients") if "ingredients" in raw else None,
        name_provided="name" in raw,
        yield_quantity_provided="yield_quantity" in raw,
        is_active_provided="is_active" in raw,
        ingredients_provided="ingredients" in raw,
    )
    return success_response(data=data)


def delete_recipe(recipe_id: str):
    return success_response(data=RecipeService.delete_recipe(recipe_id))
