"""Related accessory items for mobile / electronics (BIZ-30)."""

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.extensions import db
from app.models.item_accessory import ItemAccessory
from app.repositories.item_accessory_repository import ItemAccessoryRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.item_service import ItemService
from app.services.module_service import ModuleService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "warranty"


class ItemAccessoryService:
    @staticmethod
    def _require_module():
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        return ctx

    @staticmethod
    def list_accessories(item_id: str):
        require_permission(PERM_ITEMS_READ)
        ctx = ItemAccessoryService._require_module()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        links = ItemAccessoryRepository.list_for_item(ctx.tenant_id, item.id)
        return [
            {
                **ItemService.serialize(link.accessory),
                "sort_order": link.sort_order,
            }
            for link in links
            if link.accessory is not None and link.accessory.is_active
        ]

    @staticmethod
    def replace_accessories(item_id: str, accessory_item_ids: list[str]):
        require_permission(PERM_ITEMS_WRITE)
        ctx = ItemAccessoryService._require_module()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")

        cleaned: list[str] = []
        seen = set()
        for raw in accessory_item_ids or []:
            aid = (raw or "").strip()
            if not aid or aid in seen:
                continue
            if aid == item.id:
                raise ValidationError("An item cannot be its own accessory")
            seen.add(aid)
            cleaned.append(aid)

        for aid in cleaned:
            accessory = ItemRepository.get_by_id_and_tenant(aid, ctx.tenant_id)
            if accessory is None or not accessory.is_active:
                raise ValidationError("Accessory item not found or inactive")

        ItemAccessoryRepository.delete_for_item(ctx.tenant_id, item.id)
        for index, aid in enumerate(cleaned):
            ItemAccessoryRepository.add(
                ItemAccessory(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    item_id=item.id,
                    accessory_item_id=aid,
                    sort_order=index,
                )
            )
        db.session.commit()
        return ItemAccessoryService.list_accessories(item.id)
