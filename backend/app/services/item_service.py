"""Item business logic with price/GST audit trails."""

from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.item import Item
from app.models.role import ROLE_BILLING_USER
from app.repositories.category_repository import CategoryRepository
from app.repositories.item_repository import ItemRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_request_context


class ItemService:
    @staticmethod
    def list_items(*, q=None, category_id=None, is_active=None, page=1, per_page=50):
        ctx = require_request_context()
        if ctx.role == ROLE_BILLING_USER:
            is_active = True

        items, total = ItemRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            category_id=category_id,
            is_active=is_active,
            page=page,
            per_page=per_page,
        )
        return (
            [ItemService.serialize(i) for i in items],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_item(item_id: str):
        ctx = require_request_context()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        if ctx.role == ROLE_BILLING_USER and not item.is_active:
            raise NotFoundError("Item not found")
        return ItemService.serialize(item)

    @staticmethod
    def create_item(*, name, category_id, description, price, gst_percentage):
        ctx = require_request_context()
        name = (name or "").strip()
        if not name:
            raise ValidationError("Item name is required")

        category = CategoryRepository.get_by_id_and_tenant(category_id, ctx.tenant_id)
        if category is None:
            raise ValidationError("Category not found")
        if not category.is_active:
            raise ValidationError("Cannot add item to an inactive category")

        if ItemRepository.find_by_tenant_and_name(ctx.tenant_id, name):
            raise ConflictError("Item with this name already exists")

        price_dec = ItemService._parse_money(price, "price")
        gst_dec = ItemService._parse_gst(gst_percentage)

        item = Item(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            category_id=category.id,
            name=name,
            description=(description or "").strip() or None,
            price=price_dec,
            gst_percentage=gst_dec,
            is_active=True,
        )
        ItemRepository.add(item)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_ITEM",
            entity_type="ITEM",
            entity_id=item.id,
            new_data=ItemService.serialize(item),
        )
        db.session.commit()
        return ItemService.serialize(item)

    @staticmethod
    def update_item(
        item_id: str,
        *,
        name=None,
        category_id=None,
        description=None,
        price=None,
        gst_percentage=None,
    ):
        ctx = require_request_context()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")

        old = ItemService.serialize(item)
        price_changed = False
        gst_changed = False

        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationError("Item name is required")
            existing = ItemRepository.find_by_tenant_and_name(ctx.tenant_id, name)
            if existing and existing.id != item.id:
                raise ConflictError("Item with this name already exists")
            item.name = name

        if category_id is not None:
            category = CategoryRepository.get_by_id_and_tenant(category_id, ctx.tenant_id)
            if category is None:
                raise ValidationError("Category not found")
            item.category_id = category.id

        if description is not None:
            item.description = description.strip() or None

        if price is not None:
            new_price = ItemService._parse_money(price, "price")
            if Decimal(item.price) != new_price:
                price_changed = True
            item.price = new_price

        if gst_percentage is not None:
            new_gst = ItemService._parse_gst(gst_percentage)
            if Decimal(item.gst_percentage) != new_gst:
                gst_changed = True
            item.gst_percentage = new_gst

        new_data = ItemService.serialize(item)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_ITEM",
            entity_type="ITEM",
            entity_id=item.id,
            old_data=old,
            new_data=new_data,
        )
        if price_changed:
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="UPDATE_PRICE",
                entity_type="ITEM",
                entity_id=item.id,
                old_data={"price": old["price"]},
                new_data={"price": new_data["price"]},
            )
        if gst_changed:
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="CHANGE_GST",
                entity_type="ITEM",
                entity_id=item.id,
                old_data={"gst_percentage": old["gst_percentage"]},
                new_data={"gst_percentage": new_data["gst_percentage"]},
            )

        db.session.commit()
        return new_data

    @staticmethod
    def set_status(item_id: str, is_active: bool):
        ctx = require_request_context()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")

        old = ItemService.serialize(item)
        item.is_active = bool(is_active)
        action = "DEACTIVATE_ITEM" if not item.is_active else "UPDATE_ITEM"
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action=action,
            entity_type="ITEM",
            entity_id=item.id,
            old_data=old,
            new_data=ItemService.serialize(item),
        )
        db.session.commit()
        return ItemService.serialize(item)

    @staticmethod
    def _parse_money(value, field_name: str) -> Decimal:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError(f"Invalid {field_name}") from exc
        if amount < 0:
            raise ValidationError(f"{field_name} cannot be negative")
        return amount.quantize(Decimal("0.01"))

    @staticmethod
    def _parse_gst(value) -> Decimal:
        try:
            gst = Decimal(str(value if value is not None else "0"))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError("Invalid GST percentage") from exc
        if gst < 0 or gst > 100:
            raise ValidationError("GST percentage must be between 0 and 100")
        return gst.quantize(Decimal("0.01"))

    @staticmethod
    def serialize(item: Item):
        return {
            "id": item.id,
            "category_id": item.category_id,
            "category_name": item.category.name if item.category else None,
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "gst_percentage": float(item.gst_percentage),
            "is_active": item.is_active,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }