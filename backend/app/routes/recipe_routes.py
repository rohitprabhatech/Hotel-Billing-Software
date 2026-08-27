"""Recipe routes (BIZ-16)."""

from flask import Blueprint

from app.constants.permissions import PERM_RECIPES_READ, PERM_RECIPES_WRITE
from app.controllers import recipe_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")

# BILLING_USER allowed at role layer; hotel-only extra perms enforce industry scope.
_OPS = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)


@recipes_bp.get("")
@roles_required(*_OPS)
@module_required("recipe")
@permission_required(PERM_RECIPES_READ)
def list_recipes():
    return recipe_controller.list_recipes()


@recipes_bp.post("")
@roles_required(*_OPS)
@module_required("recipe")
@permission_required(PERM_RECIPES_WRITE)
def create_recipe():
    return recipe_controller.create_recipe()


@recipes_bp.get("/by-menu-item/<menu_item_id>")
@roles_required(*_OPS)
@module_required("recipe")
@permission_required(PERM_RECIPES_READ)
def get_recipe_by_menu_item(menu_item_id):
    return recipe_controller.get_recipe_by_menu_item(menu_item_id)


@recipes_bp.get("/<recipe_id>")
@roles_required(*_OPS)
@module_required("recipe")
@permission_required(PERM_RECIPES_READ)
def get_recipe(recipe_id):
    return recipe_controller.get_recipe(recipe_id)


@recipes_bp.put("/<recipe_id>")
@roles_required(*_OPS)
@module_required("recipe")
@permission_required(PERM_RECIPES_WRITE)
def update_recipe(recipe_id):
    return recipe_controller.update_recipe(recipe_id)


@recipes_bp.delete("/<recipe_id>")
@roles_required(*_OPS)
@module_required("recipe")
@permission_required(PERM_RECIPES_WRITE)
def delete_recipe(recipe_id):
    return recipe_controller.delete_recipe(recipe_id)
