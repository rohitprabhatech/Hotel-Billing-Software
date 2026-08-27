"""Expand menu sales into ingredient deductions (BIZ-16).

Policy: ingredients deduct at settle/bill finalize — not at KOT fire.
See app.constants.recipes.RECIPE_DEDUCTION_POLICY.
"""

from decimal import Decimal

from app.repositories.recipe_repository import RecipeRepository
from app.utils.money import qty


class RecipeStockService:
    @staticmethod
    def expand_for_deduction(tenant_id: str, sold: dict[str, Decimal]) -> dict[str, Decimal]:
        """Map sold catalog item quantities to stock item quantities via recipes.

        When the production module is enabled (bakery), ingredients are consumed at
        production time — selling deducts finished-goods stock instead.
        """
        if not sold:
            return {}
        from app.repositories.tenant_repository import TenantRepository
        from app.services.module_service import ModuleService

        tenant = TenantRepository.get_by_id(tenant_id)
        if tenant and ModuleService.is_enabled_for_tenant(tenant, "production"):
            return {str(item_id): qty(sold_qty) for item_id, sold_qty in sold.items()}

        recipes = RecipeRepository.map_active_by_menu_item_ids(tenant_id, list(sold.keys()))
        expanded: dict[str, Decimal] = {}
        for item_id, sold_qty in sold.items():
            recipe = recipes.get(item_id)
            if recipe is None:
                expanded[item_id] = expanded.get(item_id, Decimal("0")) + qty(sold_qty)
                continue
            yield_qty = qty(recipe.yield_quantity)
            if yield_qty <= 0:
                # Corrupt/legacy recipe — fall back to finished-goods deduction.
                expanded[item_id] = expanded.get(item_id, Decimal("0")) + qty(sold_qty)
                continue
            for line in recipe.ingredients:
                needed = qty(qty(sold_qty) * qty(line.quantity) / yield_qty)
                if needed <= 0:
                    continue
                expanded[line.ingredient_item_id] = expanded.get(line.ingredient_item_id, Decimal("0")) + needed
            # When a recipe has no ingredient lines, still deduct the sold dish stock.
            if not recipe.ingredients:
                expanded[item_id] = expanded.get(item_id, Decimal("0")) + qty(sold_qty)
        return expanded

    @staticmethod
    def expand_from_lines(tenant_id: str, lines: list) -> dict[str, Decimal]:
        sold: dict[str, Decimal] = {}
        for line in lines:
            item_id = getattr(line, "item_id", None) or line.get("item_id")
            quantity = getattr(line, "quantity", None) or line.get("quantity")
            if not item_id:
                continue
            sold[str(item_id)] = sold.get(str(item_id), Decimal("0")) + qty(quantity)
        return RecipeStockService.expand_for_deduction(tenant_id, sold)
