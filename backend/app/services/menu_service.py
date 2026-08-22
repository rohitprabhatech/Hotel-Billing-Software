"""Restaurant menu listing (BIZ-11)."""

from app.constants.permissions import PERM_ITEMS_READ
from app.repositories.category_repository import CategoryRepository
from app.repositories.item_repository import ItemRepository
from app.services.category_service import CategoryService
from app.services.item_service import ItemService
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class MenuService:
    @staticmethod
    def list_menu(*, is_veg=None):
        require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        veg_filter = None
        if is_veg is not None:
            veg_filter = bool(is_veg)

        items = ItemRepository.list_menu_items_by_tenant(ctx.tenant_id, is_veg=veg_filter)
        categories = CategoryRepository.list_by_tenant(ctx.tenant_id, active_only=False)
        by_id = {category.id: category for category in categories}

        grouped: dict[str, dict] = {}
        for item in items:
            category = item.category
            bucket = grouped.get(item.category_id)
            if bucket is None:
                hierarchy_path = None
                if category is not None:
                    hierarchy_path = CategoryService._hierarchy_path(category, by_id=by_id)
                bucket = {
                    "category_id": item.category_id,
                    "category_name": category.name if category else None,
                    "category_hierarchy_path": hierarchy_path,
                    "items": [],
                }
                grouped[item.category_id] = bucket
            bucket["items"].append(MenuService._serialize_menu_item(item))

        sections = sorted(
            grouped.values(),
            key=lambda row: (row["category_hierarchy_path"] or row["category_name"] or "").lower(),
        )
        return sections

    @staticmethod
    def _serialize_menu_item(item):
        data = ItemService.serialize(item)
        return {
            "id": data["id"],
            "name": data["name"],
            "description": data["description"],
            "price": data["price"],
            "gst_percentage": data["gst_percentage"],
            "uom": data["uom"],
            "is_veg": data["is_veg"],
            "is_menu": data["is_menu"],
            "category_id": data["category_id"],
            "category_name": data["category_name"],
            "category_hierarchy_path": data["category_hierarchy_path"],
        }
