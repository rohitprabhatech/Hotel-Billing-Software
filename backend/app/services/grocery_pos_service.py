"""Grocery fast POS catalog (BIZ-20 / BIZ-21)."""

from app.constants.grocery import WEIGHT_UOMS, is_weight_uom
from app.constants.perf import POS_CATALOG_DEFAULT_LIMIT, clamp_pos_catalog_limit
from app.constants.permissions import PERM_ITEMS_READ
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.bulk_pricing_service import BulkPricingService
from app.services.item_service import ItemService
from app.services.module_service import ModuleService
from app.utils.exceptions import NotFoundError
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class GroceryPosService:
    @staticmethod
    def pos_catalog(*, q: str | None = None, limit: int = POS_CATALOG_DEFAULT_LIMIT, customer_id: str | None = None):
        require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, "barcode_pos")
        rows, _ = ItemRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            is_active=True,
            page=1,
            per_page=clamp_pos_catalog_limit(limit),
        )
        bulk_enabled = bool(
            ModuleService.is_enabled_for_tenant(tenant, "bulk_pricing")
        )
        list_enabled = bool(
            ModuleService.is_enabled_for_tenant(tenant, "price_lists")
        )
        tiers_by_item = {}
        if bulk_enabled and rows:
            tiers_by_item = BulkPricingService.serialize_tiers_for_items(
                ctx.tenant_id, [row.id for row in rows]
            )
        resolved_prices = {}
        if list_enabled and rows:
            from app.services.price_list_service import PriceListService

            resolved_prices = PriceListService.resolve_catalog_prices(
                tenant, rows, customer_id=customer_id
            )
        return {
            "items": [
                GroceryPosService._serialize_pos_item(
                    row,
                    price_tiers=tiers_by_item.get(row.id) or [],
                    list_price=float(resolved_prices[row.id])
                    if row.id in resolved_prices
                    else None,
                )
                for row in rows
            ],
            "scan_defaults": {
                "weight_uoms": sorted(WEIGHT_UOMS),
                "qty_step_weight": 0.001,
                "qty_step_pcs": 1,
            },
            "bulk_pricing_enabled": bulk_enabled,
            "price_lists_enabled": list_enabled,
        }

    @staticmethod
    def _serialize_pos_item(item, *, price_tiers=None, list_price=None):
        data = ItemService.serialize(item)
        uom = data.get("uom") or "pcs"
        catalog_price = data["price"]
        effective_base = list_price if list_price is not None else catalog_price
        return {
            "id": data["id"],
            "name": data["name"],
            "barcode": data.get("barcode"),
            "sku": data.get("sku"),
            "isbn": data.get("isbn"),
            "author": data.get("author"),
            "publisher": data.get("publisher"),
            "price": catalog_price,
            "list_price": list_price,
            "base_price": effective_base,
            "gst_percentage": data["gst_percentage"],
            "uom": uom,
            "is_weight_uom": is_weight_uom(uom),
            "stock_quantity": data.get("stock_quantity"),
            "category_id": data.get("category_id"),
            "category_name": data.get("category_name"),
            "price_tiers": price_tiers or [],
        }
