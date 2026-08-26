"""Clothing POS catalog with variant stock matrix (BIZ-26)."""

from app.constants.perf import POS_CATALOG_DEFAULT_LIMIT, clamp_pos_catalog_limit
from app.constants.permissions import PERM_ITEMS_READ
from app.repositories.item_image_repository import ItemImageRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.item_variant_repository import ItemVariantRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.item_image_service import ItemImageService
from app.services.item_service import ItemService
from app.services.module_service import ModuleService
from app.services.variant_service import VariantService
from app.utils.exceptions import NotFoundError
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class ClothingPosService:
    @staticmethod
    def pos_catalog(*, q: str | None = None, limit: int = POS_CATALOG_DEFAULT_LIMIT):
        require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, "variants")
        images_enabled = ModuleService.is_enabled_for_tenant(tenant, "product_images")

        rows, _ = ItemRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            is_active=True,
            page=1,
            per_page=clamp_pos_catalog_limit(limit),
        )
        item_ids = [row.id for row in rows]
        variants_by_item = ItemVariantRepository.list_active_for_items(ctx.tenant_id, item_ids)

        primaries = {}
        if images_enabled and item_ids:
            primaries = ItemImageRepository.primary_by_item_ids(ctx.tenant_id, item_ids)

        catalog = []
        for item in rows:
            variants = [
                VariantService.serialize(row, item_name=item.name)
                for row in variants_by_item.get(item.id) or []
            ]
            sizes = sorted({row["size"] for row in variants}, key=lambda value: value.lower())
            colors = sorted({row["color"] for row in variants}, key=lambda value: value.lower())
            primary = primaries.get(item.id) if images_enabled else None
            data = ItemService.serialize(item)
            catalog.append(
                {
                    "id": data["id"],
                    "name": data["name"],
                    "price": data["price"],
                    "gst_percentage": data["gst_percentage"],
                    "sku": data.get("sku"),
                    "barcode": data.get("barcode"),
                    "stock_quantity": data.get("stock_quantity"),
                    "tracks_variants": data.get("tracks_variants"),
                    "category_id": data.get("category_id"),
                    "category_name": data.get("category_name"),
                    "primary_image_url": ItemImageService.public_url(primary) if primary else None,
                    "variants": variants,
                    "sizes": sizes,
                    "colors": colors,
                }
            )
        return {"items": catalog}
