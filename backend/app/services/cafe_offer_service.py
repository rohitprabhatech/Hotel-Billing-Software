"""Cafe add-on and combo business logic (BIZ-17)."""

from decimal import Decimal

from app.constants.permissions import PERM_ADDONS_READ, PERM_ADDONS_WRITE
from app.extensions import db
from app.models.cafe_offer import Combo, ComboItem, ItemAddon, ItemAddonGroup
from app.repositories.cafe_offer_repository import AddonRepository, ComboRepository
from app.repositories.item_repository import ItemRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class AddonService:
    @staticmethod
    def list_menu_addons():
        require_permission(PERM_ADDONS_READ)
        ctx = require_request_context()
        groups = AddonRepository.list_groups_by_tenant(ctx.tenant_id)
        return [AddonService.serialize_group(group) for group in groups]

    @staticmethod
    def create_group(*, menu_item_id: str, name: str, is_required=False, max_selections=None, addons: list[dict]):
        require_permission(PERM_ADDONS_WRITE)
        ctx = require_request_context()
        menu_item = ItemRepository.get_by_id_and_tenant(menu_item_id.strip(), ctx.tenant_id)
        if menu_item is None or not menu_item.is_active or not menu_item.is_menu:
            raise ValidationError("Menu item not found or inactive")

        group = ItemAddonGroup(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            menu_item_id=menu_item.id,
            name=(name or "").strip(),
            is_required=bool(is_required),
            max_selections=int(max_selections) if max_selections not in (None, "") else None,
            is_active=True,
        )
        if not group.name:
            raise ValidationError("Group name is required")
        AddonService._set_addons(group, addons or [], ctx.tenant_id)
        AddonRepository.add_group(group)
        serialized = AddonService.serialize_group(group)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_ADDON_GROUP",
            entity_type="ITEM_ADDON_GROUP",
            entity_id=group.id,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def delete_group(group_id: str):
        require_permission(PERM_ADDONS_WRITE)
        ctx = require_request_context()
        group = AddonRepository.get_group_by_id(ctx.tenant_id, group_id)
        if group is None:
            raise NotFoundError("Add-on group not found")
        old = AddonService.serialize_group(group)
        AddonRepository.delete_group(group)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_ADDON_GROUP",
            entity_type="ITEM_ADDON_GROUP",
            entity_id=group_id,
            old_data=old,
        )
        db.session.commit()
        return {"id": group_id, "deleted": True}

    @staticmethod
    def resolve_addons_for_menu_item(tenant_id: str, menu_item_id: str, addon_ids: list[str]) -> list[ItemAddon]:
        if not addon_ids:
            return []
        rows = AddonRepository.get_addons_by_ids(tenant_id, addon_ids)
        by_id = {row.id: row for row in rows}
        resolved = []
        for addon_id in addon_ids:
            addon = by_id.get(addon_id)
            if addon is None:
                raise ValidationError(f"Add-on not found: {addon_id}")
            if addon.group.menu_item_id != menu_item_id:
                raise ValidationError(f"Add-on {addon.name} is not valid for this menu item")
            resolved.append(addon)
        groups: dict[str, list[ItemAddon]] = {}
        for addon in resolved:
            groups.setdefault(addon.group_id, []).append(addon)
        for group_id, selected in groups.items():
            group = selected[0].group
            if group.max_selections and len(selected) > group.max_selections:
                raise ValidationError(f"Too many selections for {group.name}")
        required_groups = AddonRepository.list_groups_for_menu_items(tenant_id, [menu_item_id])
        for group in required_groups:
            if group.is_required and group.id not in groups:
                raise ValidationError(f"Add-on group '{group.name}' is required")
        return resolved

    @staticmethod
    def _set_addons(group: ItemAddonGroup, addons: list[dict], tenant_id: str):
        group.addons.clear()
        for index, row in enumerate(addons):
            name = (row.get("name") or "").strip()
            if not name:
                raise ValidationError("Add-on name is required")
            linked_item_id = (row.get("linked_item_id") or "").strip() or None
            if linked_item_id:
                item = ItemRepository.get_by_id_and_tenant(linked_item_id, tenant_id)
                if item is None or not item.is_active:
                    raise ValidationError(f"Linked item not found: {linked_item_id}")
            group.addons.append(
                ItemAddon(
                    id=new_uuid(),
                    tenant_id=tenant_id,
                    group_id=group.id,
                    name=name,
                    extra_price=money(row.get("extra_price") or 0),
                    linked_item_id=linked_item_id,
                    is_default=bool(row.get("is_default")),
                    sort_order=index,
                    is_active=True,
                )
            )

    @staticmethod
    def serialize_group(group: ItemAddonGroup):
        return {
            "id": group.id,
            "menu_item_id": group.menu_item_id,
            "menu_item_name": group.menu_item.name if group.menu_item else None,
            "name": group.name,
            "is_required": group.is_required,
            "max_selections": group.max_selections,
            "sort_order": group.sort_order,
            "is_active": group.is_active,
            "addons": [
                {
                    "id": addon.id,
                    "name": addon.name,
                    "extra_price": float(addon.extra_price),
                    "linked_item_id": addon.linked_item_id,
                    "linked_item_name": addon.linked_item.name if addon.linked_item else None,
                    "is_default": addon.is_default,
                    "sort_order": addon.sort_order,
                    "is_active": addon.is_active,
                }
                for addon in group.addons
            ],
        }


class ComboService:
    @staticmethod
    def list_combos(*, popular_only=False):
        require_permission(PERM_ADDONS_READ)
        ctx = require_request_context()
        rows = ComboRepository.list_by_tenant(ctx.tenant_id, popular_only=popular_only)
        return [ComboService.serialize(row) for row in rows]

    @staticmethod
    def get_combo(combo_id: str):
        require_permission(PERM_ADDONS_READ)
        ctx = require_request_context()
        combo = ComboRepository.get_by_id(ctx.tenant_id, combo_id)
        if combo is None:
            raise NotFoundError("Combo not found")
        return ComboService.serialize(combo)

    @staticmethod
    def create_combo(*, name: str, combo_price, description=None, is_popular=False, items: list[dict]):
        require_permission(PERM_ADDONS_WRITE)
        ctx = require_request_context()
        parsed_name = (name or "").strip()
        if not parsed_name:
            raise ValidationError("Combo name is required")
        existing = (
            db.session.query(Combo)
            .filter(Combo.tenant_id == ctx.tenant_id, Combo.name == parsed_name)
            .first()
        )
        if existing:
            raise ConflictError("A combo with this name already exists")

        combo = Combo(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            name=parsed_name,
            description=(description or "").strip() or None,
            combo_price=money(combo_price),
            is_popular=bool(is_popular),
            is_active=True,
            created_by=ctx.user_id,
        )
        ComboService._set_items(combo, items or [], ctx.tenant_id)
        ComboRepository.add(combo)
        serialized = ComboService.serialize(combo)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_COMBO",
            entity_type="COMBO",
            entity_id=combo.id,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def delete_combo(combo_id: str):
        require_permission(PERM_ADDONS_WRITE)
        ctx = require_request_context()
        combo = ComboRepository.get_by_id(ctx.tenant_id, combo_id)
        if combo is None:
            raise NotFoundError("Combo not found")
        old = ComboService.serialize(combo)
        ComboRepository.delete(combo)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_COMBO",
            entity_type="COMBO",
            entity_id=combo_id,
            old_data=old,
        )
        db.session.commit()
        return {"id": combo_id, "deleted": True}

    @staticmethod
    def expand_combo_lines(tenant_id: str, combo_id: str, quantity) -> list[dict]:
        combo = ComboRepository.get_by_id(tenant_id, combo_id)
        if combo is None or not combo.is_active:
            raise ValidationError("Combo not found or inactive")
        if not combo.items:
            raise ValidationError("Combo has no items")
        parsed_qty = qty(quantity)
        if parsed_qty <= 0:
            raise ValidationError("Quantity must be greater than zero")

        catalog_total = Decimal("0")
        component_rows = []
        for row in combo.items:
            item = ItemRepository.get_by_id_and_tenant(row.item_id, tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Combo item inactive: {row.item_name}")
            line_qty = qty(row.quantity * parsed_qty)
            gross = money(item.price * line_qty)
            catalog_total += gross
            component_rows.append(
                {
                    "item": item,
                    "quantity": line_qty,
                    "catalog_gross": gross,
                    "combo_id": combo.id,
                }
            )

        target_total = money(combo.combo_price * parsed_qty)
        lines = []
        allocated = Decimal("0")
        for index, row in enumerate(component_rows):
            if index == len(component_rows) - 1:
                line_gross = money(target_total - allocated)
            elif catalog_total > 0:
                line_gross = money(target_total * (row["catalog_gross"] / catalog_total))
                allocated += line_gross
            else:
                line_gross = money(target_total / len(component_rows))
                allocated += line_gross
            unit_price = money(line_gross / row["quantity"]) if row["quantity"] else money(0)
            lines.append(
                {
                    "item_id": row["item"].id,
                    "quantity": row["quantity"],
                    "unit_price": unit_price,
                    "combo_id": combo.id,
                    "addon_ids": [],
                }
            )
        return lines

    @staticmethod
    def _set_items(combo: Combo, items: list[dict], tenant_id: str):
        if not items:
            raise ValidationError("Combo requires at least one item")
        combo.items.clear()
        for index, row in enumerate(items):
            item_id = (row.get("item_id") or "").strip()
            if not item_id:
                raise ValidationError("item_id is required for combo lines")
            item = ItemRepository.get_by_id_and_tenant(item_id, tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item not found or inactive: {item_id}")
            parsed_qty = qty(row.get("quantity") or 1)
            if parsed_qty <= 0:
                raise ValidationError("Quantity must be greater than zero")
            combo.items.append(
                ComboItem(
                    id=new_uuid(),
                    tenant_id=tenant_id,
                    combo_id=combo.id,
                    item_id=item.id,
                    item_name=item.name,
                    quantity=parsed_qty,
                    sort_order=index,
                )
            )

    @staticmethod
    def serialize(combo: Combo):
        catalog_total = float(
            sum(float(row.quantity) * float(row.item.price if row.item else 0) for row in combo.items)
            if combo.items
            else 0
        )
        return {
            "id": combo.id,
            "name": combo.name,
            "description": combo.description,
            "combo_price": float(combo.combo_price),
            "catalog_total": catalog_total,
            "savings": max(0.0, catalog_total - float(combo.combo_price)),
            "is_popular": combo.is_popular,
            "is_active": combo.is_active,
            "items": [
                {
                    "id": row.id,
                    "item_id": row.item_id,
                    "item_name": row.item_name,
                    "quantity": float(row.quantity),
                    "sort_order": row.sort_order,
                }
                for row in combo.items
            ],
            "created_at": combo.created_at.isoformat() if combo.created_at else None,
            "updated_at": combo.updated_at.isoformat() if combo.updated_at else None,
        }


class CafeMenuService:
    @staticmethod
    def quick_pos_catalog():
        require_permission(PERM_ADDONS_READ)
        ctx = require_request_context()

        menu_items = ItemRepository.list_menu_items_by_tenant(ctx.tenant_id)
        groups = AddonRepository.list_groups_for_menu_items(ctx.tenant_id, [row.id for row in menu_items])
        groups_by_item: dict[str, list] = {}
        for group in groups:
            groups_by_item.setdefault(group.menu_item_id, []).append(AddonService.serialize_group(group))
        combos = ComboRepository.list_by_tenant(ctx.tenant_id)
        popular_combos = [ComboService.serialize(row) for row in combos if row.is_popular]
        return {
            "menu_items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "price": float(item.price),
                    "is_veg": item.is_veg,
                    "gst_percentage": float(item.gst_percentage),
                    "addon_groups": groups_by_item.get(item.id, []),
                }
                for item in menu_items
            ],
            "combos": [ComboService.serialize(row) for row in combos],
            "popular_combos": popular_combos,
        }
