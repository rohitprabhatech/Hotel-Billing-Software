"""Bulk pricing / item price tiers (BIZ-21)."""

from decimal import Decimal

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.extensions import db
from app.models.item_price_tier import ItemPriceTier
from app.repositories.item_price_tier_repository import ItemPriceTierRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class BulkPricingService:
    MODULE = "bulk_pricing"

    @staticmethod
    def _require_module():
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, BulkPricingService.MODULE)
        return ctx, tenant

    @staticmethod
    def _get_item(tenant_id: str, item_id: str):
        item = ItemRepository.get_by_id_and_tenant(item_id.strip(), tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        return item

    @staticmethod
    def serialize_tier(tier: ItemPriceTier) -> dict:
        return {
            "id": tier.id,
            "item_id": tier.item_id,
            "min_quantity": float(tier.min_quantity),
            "unit_price": float(tier.unit_price),
            "is_active": tier.is_active,
            "created_at": tier.created_at.isoformat() if tier.created_at else None,
            "updated_at": tier.updated_at.isoformat() if tier.updated_at else None,
        }

    @staticmethod
    def list_tiers(item_id: str):
        require_permission(PERM_ITEMS_READ)
        ctx, _ = BulkPricingService._require_module()
        BulkPricingService._get_item(ctx.tenant_id, item_id)
        rows = ItemPriceTierRepository.list_by_item(ctx.tenant_id, item_id)
        return [BulkPricingService.serialize_tier(row) for row in rows]

    @staticmethod
    def create_tier(item_id: str, *, min_quantity, unit_price, is_active: bool = True):
        require_permission(PERM_ITEMS_WRITE)
        ctx, _ = BulkPricingService._require_module()
        item = BulkPricingService._get_item(ctx.tenant_id, item_id)
        min_qty = qty(min_quantity)
        price = money(unit_price)
        if min_qty <= 0:
            raise ValidationError("min_quantity must be greater than zero")
        if price < 0:
            raise ValidationError("unit_price cannot be negative")

        existing = ItemPriceTierRepository.list_by_item(ctx.tenant_id, item.id)
        if any(Decimal(row.min_quantity) == min_qty for row in existing):
            raise ConflictError("A price tier already exists for this minimum quantity")

        tier = ItemPriceTier(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            min_quantity=min_qty,
            unit_price=price,
            is_active=bool(is_active),
        )
        ItemPriceTierRepository.add(tier)
        serialized = BulkPricingService.serialize_tier(tier)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_PRICE_TIER",
            entity_type="ITEM_PRICE_TIER",
            entity_id=tier.id,
            new_data={**serialized, "item_name": item.name},
        )
        db.session.commit()
        return serialized

    @staticmethod
    def replace_tiers(item_id: str, tiers: list[dict]):
        require_permission(PERM_ITEMS_WRITE)
        ctx, _ = BulkPricingService._require_module()
        item = BulkPricingService._get_item(ctx.tenant_id, item_id)

        old_rows = ItemPriceTierRepository.list_by_item(ctx.tenant_id, item.id)
        old_data = [BulkPricingService.serialize_tier(row) for row in old_rows]

        normalized = []
        seen = set()
        for raw in tiers or []:
            min_qty = qty(raw["min_quantity"])
            price = money(raw["unit_price"])
            if min_qty <= 0:
                raise ValidationError("min_quantity must be greater than zero")
            if price < 0:
                raise ValidationError("unit_price cannot be negative")
            key = str(min_qty)
            if key in seen:
                raise ValidationError(f"Duplicate min_quantity: {float(min_qty):g}")
            seen.add(key)
            normalized.append(
                {
                    "min_quantity": min_qty,
                    "unit_price": price,
                    "is_active": bool(raw.get("is_active", True)),
                }
            )

        ItemPriceTierRepository.delete_for_item(ctx.tenant_id, item.id)
        created = []
        for row in sorted(normalized, key=lambda r: r["min_quantity"]):
            tier = ItemPriceTier(
                id=new_uuid(),
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                min_quantity=row["min_quantity"],
                unit_price=row["unit_price"],
                is_active=row["is_active"],
            )
            ItemPriceTierRepository.add(tier)
            created.append(tier)

        new_data = [BulkPricingService.serialize_tier(row) for row in created]
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="REPLACE_PRICE_TIERS",
            entity_type="ITEM",
            entity_id=item.id,
            old_data={"tiers": old_data, "item_name": item.name},
            new_data={"tiers": new_data, "item_name": item.name},
        )
        db.session.commit()
        return new_data

    @staticmethod
    def delete_tier(item_id: str, tier_id: str):
        require_permission(PERM_ITEMS_WRITE)
        ctx, _ = BulkPricingService._require_module()
        BulkPricingService._get_item(ctx.tenant_id, item_id)
        tier = ItemPriceTierRepository.get_by_id(ctx.tenant_id, tier_id)
        if tier is None or tier.item_id != item_id:
            raise NotFoundError("Price tier not found")
        old = BulkPricingService.serialize_tier(tier)
        ItemPriceTierRepository.delete(tier)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_PRICE_TIER",
            entity_type="ITEM_PRICE_TIER",
            entity_id=tier_id,
            old_data=old,
        )
        db.session.commit()
        return {"id": tier_id, "deleted": True}

    @staticmethod
    def resolve_unit_price_for_item(tenant, item, quantity: Decimal) -> Decimal:
        """Return tier unit price when bulk_pricing is enabled; else item.price."""
        base = Decimal(item.price)
        if tenant is None or not ModuleService.is_enabled_for_tenant(tenant, BulkPricingService.MODULE):
            return base
        tiers = ItemPriceTierRepository.list_by_item(
            tenant.id, item.id, active_only=True
        )
        if not tiers:
            return base
        return ItemPriceTierRepository.resolve_unit_price(tiers, qty(quantity), base)

    @staticmethod
    def resolve_many(tenant, items_by_id: dict, quantities: dict[str, Decimal]) -> dict[str, Decimal]:
        """Map item_id -> resolved unit price for a bill."""
        result = {}
        if tenant is None or not ModuleService.is_enabled_for_tenant(tenant, BulkPricingService.MODULE):
            for item_id, item in items_by_id.items():
                result[item_id] = Decimal(item.price)
            return result

        tiers_by_item = ItemPriceTierRepository.list_by_item_ids(
            tenant.id, list(items_by_id.keys()), active_only=True
        )
        for item_id, item in items_by_id.items():
            base = Decimal(item.price)
            tiers = tiers_by_item.get(item_id) or []
            quantity = quantities.get(item_id) or Decimal("0")
            result[item_id] = ItemPriceTierRepository.resolve_unit_price(tiers, qty(quantity), base)
        return result

    @staticmethod
    def serialize_tiers_for_items(tenant_id: str, item_ids: list[str]) -> dict[str, list[dict]]:
        grouped = ItemPriceTierRepository.list_by_item_ids(
            tenant_id, item_ids, active_only=True
        )
        return {
            item_id: [BulkPricingService.serialize_tier(row) for row in rows]
            for item_id, rows in grouped.items()
        }
