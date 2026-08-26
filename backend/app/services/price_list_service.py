"""Wholesale price list engine (BIZ-51).

Resolution order (documented):
1. Customer-assigned price list item price
2. Default WHOLESALE price list item price
3. Bulk quantity tiers on catalog retail price (BIZ-21)
4. Catalog retail (`items.price`)
"""

from decimal import Decimal

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.extensions import db
from app.models.price_list import (
    LIST_TYPE_WHOLESALE,
    CustomerPriceList,
    PriceList,
    PriceListItem,
)
from app.models.role import ROLE_BILLING_USER
from app.repositories.customer_repository import CustomerRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.price_list_repository import PriceListRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.bulk_pricing_service import BulkPricingService
from app.services.module_service import ModuleService
from app.utils.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "price_lists"


class PriceListService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_ITEMS_READ if not write else PERM_ITEMS_WRITE)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage price lists")
        return ctx, tenant

    @staticmethod
    def _serialize_item(row: PriceListItem) -> dict:
        item = row.item
        return {
            "id": row.id,
            "item_id": row.item_id,
            "item_name": item.name if item else None,
            "unit_price": float(row.unit_price),
            "is_active": row.is_active,
        }

    @staticmethod
    def serialize(row: PriceList, *, include_items=False) -> dict:
        data = {
            "id": row.id,
            "name": row.name,
            "list_type": row.list_type,
            "is_default": row.is_default,
            "is_active": row.is_active,
            "notes": row.notes,
            "item_count": len(row.items or []) if include_items else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
        if include_items:
            data["items"] = [PriceListService._serialize_item(line) for line in (row.items or [])]
        return data

    @staticmethod
    def serialize_assignment(row: CustomerPriceList) -> dict:
        customer = row.customer
        price_list = row.price_list
        return {
            "id": row.id,
            "customer_id": row.customer_id,
            "customer_name": customer.name if customer else None,
            "price_list_id": row.price_list_id,
            "price_list_name": price_list.name if price_list else None,
            "assigned_at": row.assigned_at.isoformat() if row.assigned_at else None,
        }

    @staticmethod
    def list_price_lists(*, list_type=None, page=1, per_page=100):
        ctx, _ = PriceListService._require(write=False)
        rows, total = PriceListRepository.list_for_tenant(
            ctx.tenant_id,
            list_type=list_type,
            page=page,
            per_page=per_page,
        )
        return (
            [PriceListService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get_price_list(price_list_id: str):
        ctx, _ = PriceListService._require(write=False)
        row = PriceListRepository.get_by_id(ctx.tenant_id, price_list_id)
        if row is None:
            raise NotFoundError("Price list not found")
        return PriceListService.serialize(row, include_items=True)

    @staticmethod
    def create(*, name, list_type=LIST_TYPE_WHOLESALE, is_default=False, is_active=True, notes=None):
        ctx, _ = PriceListService._require(write=True)
        label = (name or "").strip()
        if not label:
            raise ValidationError("Name is required")
        list_code = (list_type or LIST_TYPE_WHOLESALE).strip().upper()

        row = PriceList(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            name=label,
            list_type=list_code,
            is_default=bool(is_default),
            is_active=bool(is_active),
            notes=(notes or "").strip() or None,
        )
        if row.is_default:
            PriceListRepository.clear_default_for_type(ctx.tenant_id, list_code)
        PriceListRepository.add(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_PRICE_LIST",
            entity_type="PRICE_LIST",
            entity_id=row.id,
            new_data=PriceListService.serialize(row),
        )
        db.session.commit()
        db.session.refresh(row)
        return PriceListService.serialize(row)

    @staticmethod
    def update(price_list_id: str, **fields):
        ctx, _ = PriceListService._require(write=True)
        row = PriceListRepository.get_by_id(ctx.tenant_id, price_list_id)
        if row is None:
            raise NotFoundError("Price list not found")
        old = PriceListService.serialize(row)

        if fields.get("name") is not None:
            label = (fields["name"] or "").strip()
            if not label:
                raise ValidationError("Name is required")
            row.name = label
        if fields.get("list_type") is not None:
            row.list_type = (fields["list_type"] or LIST_TYPE_WHOLESALE).strip().upper()
        if fields.get("is_active") is not None:
            row.is_active = bool(fields["is_active"])
        if fields.get("notes") is not None:
            row.notes = (fields["notes"] or "").strip() or None
        if fields.get("is_default") is not None:
            row.is_default = bool(fields["is_default"])
            if row.is_default:
                PriceListRepository.clear_default_for_type(
                    ctx.tenant_id, row.list_type, except_id=row.id
                )

        serialized = PriceListService.serialize(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_PRICE_LIST",
            entity_type="PRICE_LIST",
            entity_id=row.id,
            old_data=old,
            new_data=serialized,
        )
        db.session.commit()
        db.session.refresh(row)
        return serialized

    @staticmethod
    def delete(price_list_id: str):
        ctx, _ = PriceListService._require(write=True)
        row = PriceListRepository.get_by_id(ctx.tenant_id, price_list_id)
        if row is None:
            raise NotFoundError("Price list not found")
        old = PriceListService.serialize(row, include_items=True)
        assignments = PriceListRepository.list_assignments(ctx.tenant_id, price_list_id=row.id)
        if assignments:
            raise ConflictError("Remove customer assignments before deleting this price list")
        PriceListRepository.delete(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_PRICE_LIST",
            entity_type="PRICE_LIST",
            entity_id=price_list_id,
            old_data=old,
        )
        db.session.commit()
        return {"id": price_list_id, "deleted": True}

    @staticmethod
    def replace_items(price_list_id: str, items: list[dict]):
        ctx, _ = PriceListService._require(write=True)
        row = PriceListRepository.get_by_id(ctx.tenant_id, price_list_id)
        if row is None:
            raise NotFoundError("Price list not found")

        old_items = [
            PriceListService._serialize_item(line)
            for line in PriceListRepository.list_items(ctx.tenant_id, price_list_id)
        ]

        normalized = []
        seen = set()
        for raw in items or []:
            item_id = (raw.get("item_id") or "").strip()
            if not item_id:
                raise ValidationError("item_id is required on each line")
            if item_id in seen:
                raise ValidationError("Duplicate item_id in price list")
            seen.add(item_id)
            item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
            if item is None or not item.is_active:
                raise ValidationError("Item not found or inactive")
            price = money(raw["unit_price"])
            if price < 0:
                raise ValidationError("unit_price cannot be negative")
            normalized.append(
                {
                    "item_id": item.id,
                    "unit_price": price,
                    "is_active": bool(raw.get("is_active", True)),
                }
            )

        PriceListRepository.delete_items_for_list(ctx.tenant_id, price_list_id)
        created = []
        for line in normalized:
            item_row = PriceListItem(
                id=new_uuid(),
                tenant_id=ctx.tenant_id,
                price_list_id=row.id,
                item_id=line["item_id"],
                unit_price=line["unit_price"],
                is_active=line["is_active"],
            )
            PriceListRepository.add(item_row)
            created.append(item_row)

        db.session.flush()
        new_items = [PriceListService._serialize_item(line) for line in created]
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="REPLACE_PRICE_LIST_ITEMS",
            entity_type="PRICE_LIST",
            entity_id=row.id,
            old_data={"items": old_items, "name": row.name},
            new_data={"items": new_items, "name": row.name},
        )
        db.session.commit()
        return new_items

    @staticmethod
    def list_assignments(*, price_list_id=None):
        ctx, _ = PriceListService._require(write=False)
        rows = PriceListRepository.list_assignments(
            ctx.tenant_id, price_list_id=price_list_id
        )
        return [PriceListService.serialize_assignment(row) for row in rows]

    @staticmethod
    def assign_customer(customer_id: str, *, price_list_id: str):
        ctx, _ = PriceListService._require(write=True)
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")
        price_list = PriceListRepository.get_by_id(ctx.tenant_id, price_list_id.strip())
        if price_list is None or not price_list.is_active:
            raise ValidationError("Price list not found or inactive")

        existing = PriceListRepository.get_assignment(ctx.tenant_id, customer.id)
        old = PriceListService.serialize_assignment(existing) if existing else None
        if existing is None:
            existing = CustomerPriceList(
                id=new_uuid(),
                tenant_id=ctx.tenant_id,
                customer_id=customer.id,
                price_list_id=price_list.id,
            )
            PriceListRepository.add(existing)
        else:
            existing.price_list_id = price_list.id

        serialized = PriceListService.serialize_assignment(existing)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="ASSIGN_CUSTOMER_PRICE_LIST",
            entity_type="CUSTOMER",
            entity_id=customer.id,
            old_data=old,
            new_data=serialized,
        )
        db.session.commit()
        db.session.refresh(existing)
        return serialized

    @staticmethod
    def unassign_customer(customer_id: str):
        ctx, _ = PriceListService._require(write=True)
        row = PriceListRepository.get_assignment(ctx.tenant_id, customer_id.strip())
        if row is None:
            raise NotFoundError("Customer price list assignment not found")
        old = PriceListService.serialize_assignment(row)
        PriceListRepository.delete_assignment(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UNASSIGN_CUSTOMER_PRICE_LIST",
            entity_type="CUSTOMER",
            entity_id=customer_id,
            old_data=old,
        )
        db.session.commit()
        return {"customer_id": customer_id, "deleted": True}

    @staticmethod
    def resolve_many(
        tenant,
        items_by_id: dict,
        quantities: dict[str, Decimal],
        *,
        customer_id: str | None = None,
    ) -> dict[str, Decimal]:
        """Resolve bill line unit prices for wholesale tenants."""
        if tenant is None or not items_by_id:
            return {}

        if not ModuleService.is_enabled_for_tenant(tenant, MODULE):
            return BulkPricingService.resolve_many(tenant, items_by_id, quantities)

        item_ids = list(items_by_id.keys())
        customer_list_id = None
        if customer_id:
            assignment = PriceListRepository.get_assignment(tenant.id, customer_id.strip())
            if assignment:
                customer_list_id = assignment.price_list_id

        default_wholesale = PriceListRepository.get_default(tenant.id, LIST_TYPE_WHOLESALE)
        list_ids = [lid for lid in (customer_list_id, default_wholesale.id if default_wholesale else None) if lid]
        prices_by_list = PriceListRepository.items_map_for_lists(
            tenant.id, list_ids, item_ids, active_only=True
        )
        customer_prices = prices_by_list.get(customer_list_id or "", {})
        wholesale_prices = (
            prices_by_list.get(default_wholesale.id, {}) if default_wholesale else {}
        )

        bulk_prices = BulkPricingService.resolve_many(tenant, items_by_id, quantities)

        result = {}
        for item_id, item in items_by_id.items():
            if item_id in customer_prices:
                result[item_id] = customer_prices[item_id]
            elif item_id in wholesale_prices:
                result[item_id] = wholesale_prices[item_id]
            else:
                result[item_id] = bulk_prices.get(item_id, Decimal(item.price))
        return result

    @staticmethod
    def resolve_catalog_prices(
        tenant,
        items: list,
        *,
        customer_id: str | None = None,
    ) -> dict[str, Decimal]:
        """Resolve list/catalog prices at qty=1 for POS display."""
        if tenant is None or not items:
            return {}
        items_by_id = {row.id: row for row in items}
        quantities = {row.id: Decimal("1") for row in items}
        return PriceListService.resolve_many(
            tenant, items_by_id, quantities, customer_id=customer_id
        )
