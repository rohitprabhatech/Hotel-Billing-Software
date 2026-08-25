"""Size/color/brand variant catalog and stock (BIZ-25)."""

from decimal import Decimal

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.extensions import db
from app.models.item_variant import ItemVariant
from app.repositories.item_repository import ItemRepository
from app.repositories.item_variant_repository import ItemVariantRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.utils.exceptions import ConflictError, InsufficientStockError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class VariantService:
    MODULE = "variants"

    @staticmethod
    def _require_module():
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, VariantService.MODULE)
        return ctx, tenant

    @staticmethod
    def _get_item(tenant_id: str, item_id: str):
        item = ItemRepository.get_by_id_and_tenant(item_id.strip(), tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        return item

    @staticmethod
    def _norm_label(value, *, field: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValidationError(f"{field} is required")
        return text

    @staticmethod
    def _optional(value) -> str | None:
        text = (value or "").strip()
        return text or None

    @staticmethod
    def serialize(variant: ItemVariant, *, item_name: str | None = None) -> dict:
        return {
            "id": variant.id,
            "item_id": variant.item_id,
            "item_name": item_name or (variant.item.name if variant.item else None),
            "size": variant.size,
            "color": variant.color,
            "brand": variant.brand,
            "sku": variant.sku,
            "barcode": variant.barcode,
            "stock_quantity": float(variant.stock_quantity),
            "is_active": variant.is_active,
            "label": f"{variant.size} / {variant.color}",
            "created_at": variant.created_at.isoformat() if variant.created_at else None,
            "updated_at": variant.updated_at.isoformat() if variant.updated_at else None,
        }

    @staticmethod
    def _assert_unique_codes(tenant_id: str, *, sku, barcode, exclude_id=None):
        from app.repositories.item_repository import ItemRepository as Items

        if sku:
            found = ItemVariantRepository.find_by_sku(tenant_id, sku)
            if found and found.id != exclude_id:
                raise ConflictError("A variant with this SKU already exists")
            item_sku = Items.find_by_tenant_and_sku(tenant_id, sku)
            if item_sku is not None:
                raise ConflictError("SKU already used on a catalog item")
        if barcode:
            found = ItemVariantRepository.find_by_barcode(tenant_id, barcode)
            if found and found.id != exclude_id:
                raise ConflictError("A variant with this barcode already exists")
            item_bc = Items.find_by_tenant_and_barcode(tenant_id, barcode)
            if item_bc is not None:
                raise ConflictError("Barcode already used on a catalog item")

    @staticmethod
    def _sync_parent_stock(item):
        total = ItemVariantRepository.stock_sum(item.tenant_id, item.id)
        item.stock_quantity = qty(total)
        item.tracks_variants = True

    @staticmethod
    def list_for_item(item_id: str):
        require_permission(PERM_ITEMS_READ)
        ctx, _ = VariantService._require_module()
        item = VariantService._get_item(ctx.tenant_id, item_id)
        rows = ItemVariantRepository.list_by_item(ctx.tenant_id, item.id)
        return [VariantService.serialize(row, item_name=item.name) for row in rows]

    @staticmethod
    def list_all(*, item_id=None, page=1, per_page=50):
        require_permission(PERM_ITEMS_READ)
        ctx, _ = VariantService._require_module()
        rows, total = ItemVariantRepository.list_for_tenant(
            ctx.tenant_id, item_id=item_id, page=page, per_page=per_page
        )
        return (
            [VariantService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def create(item_id: str, *, size, color, brand=None, sku=None, barcode=None, stock_quantity=0, is_active=True):
        require_permission(PERM_ITEMS_WRITE)
        ctx, _ = VariantService._require_module()
        item = VariantService._get_item(ctx.tenant_id, item_id)
        if getattr(item, "tracks_serial", False):
            raise ValidationError("Serial / IMEI items cannot also track size/color variants")
        size_v = VariantService._norm_label(size, field="size")
        color_v = VariantService._norm_label(color, field="color")
        if ItemVariantRepository.find_size_color(ctx.tenant_id, item.id, size_v, color_v):
            raise ConflictError("A variant with this size and color already exists")

        sku_v = VariantService._optional(sku)
        barcode_v = VariantService._optional(barcode)
        VariantService._assert_unique_codes(ctx.tenant_id, sku=sku_v, barcode=barcode_v)

        stock = qty(stock_quantity or 0)
        if stock < 0:
            raise ValidationError("stock_quantity cannot be negative")

        existing_count = ItemVariantRepository.count_for_item(ctx.tenant_id, item.id)
        if existing_count == 0 and stock == 0 and item.stock_quantity:
            stock = qty(item.stock_quantity)

        variant = ItemVariant(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            size=size_v,
            color=color_v,
            brand=VariantService._optional(brand),
            sku=sku_v,
            barcode=barcode_v,
            stock_quantity=stock,
            is_active=bool(is_active),
        )
        ItemVariantRepository.add(variant)
        VariantService._sync_parent_stock(item)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_VARIANT",
            entity_type="ITEM_VARIANT",
            entity_id=variant.id,
            new_data=VariantService.serialize(variant, item_name=item.name),
        )
        db.session.commit()
        db.session.refresh(variant)
        return VariantService.serialize(variant, item_name=item.name)

    @staticmethod
    def replace(item_id: str, rows: list[dict]):
        require_permission(PERM_ITEMS_WRITE)
        ctx, _ = VariantService._require_module()
        item = VariantService._get_item(ctx.tenant_id, item_id)
        seen = set()
        sku_seen = set()
        barcode_seen = set()
        prepared = []
        for row in rows or []:
            size_v = VariantService._norm_label(row.get("size"), field="size")
            color_v = VariantService._norm_label(row.get("color"), field="color")
            key = (size_v.lower(), color_v.lower())
            if key in seen:
                raise ConflictError("Duplicate size and color in the variant matrix")
            seen.add(key)
            stock = qty(row.get("stock_quantity") or 0)
            if stock < 0:
                raise ValidationError("stock_quantity cannot be negative")
            sku_v = VariantService._optional(row.get("sku"))
            barcode_v = VariantService._optional(row.get("barcode"))
            if sku_v:
                sku_key = sku_v.lower()
                if sku_key in sku_seen:
                    raise ConflictError("Duplicate SKU in the variant matrix")
                sku_seen.add(sku_key)
            if barcode_v:
                barcode_key = barcode_v.lower()
                if barcode_key in barcode_seen:
                    raise ConflictError("Duplicate barcode in the variant matrix")
                barcode_seen.add(barcode_key)
            prepared.append(
                {
                    "size": size_v,
                    "color": color_v,
                    "brand": VariantService._optional(row.get("brand")),
                    "sku": sku_v,
                    "barcode": barcode_v,
                    "stock_quantity": stock,
                    "is_active": bool(row.get("is_active", True)),
                }
            )

        existing = ItemVariantRepository.list_by_item(ctx.tenant_id, item.id)
        for row in existing:
            ItemVariantRepository.delete(row)
        db.session.flush()

        for payload in prepared:
            VariantService._assert_unique_codes(
                ctx.tenant_id, sku=payload["sku"], barcode=payload["barcode"]
            )

        created = []
        for payload in prepared:
            variant = ItemVariant(id=new_uuid(), tenant_id=ctx.tenant_id, item_id=item.id, **payload)
            ItemVariantRepository.add(variant)
            created.append(variant)

        if created:
            VariantService._sync_parent_stock(item)
        else:
            item.tracks_variants = False
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="REPLACE_VARIANTS",
            entity_type="ITEM",
            entity_id=item.id,
            new_data={"count": len(created)},
        )
        db.session.commit()
        return [VariantService.serialize(row, item_name=item.name) for row in created]

    @staticmethod
    def update(item_id: str, variant_id: str, **fields):
        require_permission(PERM_ITEMS_WRITE)
        ctx, _ = VariantService._require_module()
        item = VariantService._get_item(ctx.tenant_id, item_id)
        variant = ItemVariantRepository.get_by_id(ctx.tenant_id, variant_id)
        if variant is None or variant.item_id != item.id:
            raise NotFoundError("Variant not found")

        if fields.get("size") is not None:
            variant.size = VariantService._norm_label(fields["size"], field="size")
        if fields.get("color") is not None:
            variant.color = VariantService._norm_label(fields["color"], field="color")
        clash = ItemVariantRepository.find_size_color(ctx.tenant_id, item.id, variant.size, variant.color)
        if clash and clash.id != variant.id:
            raise ConflictError("A variant with this size and color already exists")

        if "brand" in fields:
            variant.brand = VariantService._optional(fields.get("brand"))
        if "sku" in fields:
            variant.sku = VariantService._optional(fields.get("sku"))
        if "barcode" in fields:
            variant.barcode = VariantService._optional(fields.get("barcode"))
        VariantService._assert_unique_codes(
            ctx.tenant_id, sku=variant.sku, barcode=variant.barcode, exclude_id=variant.id
        )
        if fields.get("stock_quantity") is not None:
            stock = qty(fields["stock_quantity"])
            if stock < 0:
                raise ValidationError("stock_quantity cannot be negative")
            variant.stock_quantity = stock
        if fields.get("is_active") is not None:
            variant.is_active = bool(fields["is_active"])

        VariantService._sync_parent_stock(item)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_VARIANT",
            entity_type="ITEM_VARIANT",
            entity_id=variant.id,
            new_data=VariantService.serialize(variant, item_name=item.name),
        )
        db.session.commit()
        return VariantService.serialize(variant, item_name=item.name)

    @staticmethod
    def delete(item_id: str, variant_id: str):
        require_permission(PERM_ITEMS_WRITE)
        ctx, _ = VariantService._require_module()
        item = VariantService._get_item(ctx.tenant_id, item_id)
        variant = ItemVariantRepository.get_by_id(ctx.tenant_id, variant_id)
        if variant is None or variant.item_id != item.id:
            raise NotFoundError("Variant not found")
        payload = VariantService.serialize(variant, item_name=item.name)
        ItemVariantRepository.delete(variant)
        remaining = ItemVariantRepository.count_for_item(ctx.tenant_id, item.id)
        if remaining == 0:
            item.tracks_variants = False
        else:
            VariantService._sync_parent_stock(item)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_VARIANT",
            entity_type="ITEM_VARIANT",
            entity_id=variant_id,
            old_data=payload,
        )
        db.session.commit()
        return payload

    @staticmethod
    def item_tracks_variants(item) -> bool:
        if getattr(item, "tracks_variants", False):
            return True
        return ItemVariantRepository.count_for_item(item.tenant_id, item.id) > 0

    @staticmethod
    def deduct(tenant_id: str, item, variant_id: str, quantity: Decimal, *, user_id: str | None):
        if not variant_id:
            raise ValidationError(f"Select a size/color variant for {item.name}")
        variant = ItemVariantRepository.lock_by_id(tenant_id, variant_id)
        if variant is None or not variant.is_active or variant.item_id != item.id:
            raise ValidationError(f"Invalid variant for {item.name}")
        available = Decimal(variant.stock_quantity or 0)
        if quantity > available:
            NotificationService.notify_insufficient_attempt(
                tenant_id=tenant_id,
                item_name=f"{item.name} ({variant.size}/{variant.color})",
                item_id=item.id,
                available=available,
                requested=quantity,
                user_id=user_id,
            )
            db.session.commit()
            raise InsufficientStockError(
                f"Insufficient stock for {item.name} ({variant.size}/{variant.color}). "
                f"Available: {float(available):g}, requested: {float(quantity):g}.",
                details={
                    "item_id": item.id,
                    "variant_id": variant.id,
                    "available": float(available),
                    "requested": float(quantity),
                },
            )
        previous = available
        variant.stock_quantity = qty(available - quantity)
        VariantService._sync_parent_stock(item)
        NotificationService.notify_variant_stock(
            tenant_id=tenant_id,
            item=item,
            variant=variant,
            previous=previous,
            new_stock=variant.stock_quantity,
        )
        return variant

    @staticmethod
    def restore(tenant_id: str, item, variant_id: str, quantity: Decimal):
        variant = ItemVariantRepository.lock_by_id(tenant_id, variant_id)
        if variant is None or variant.item_id != item.id:
            return None
        previous = Decimal(variant.stock_quantity or 0)
        variant.stock_quantity = qty(previous + quantity)
        VariantService._sync_parent_stock(item)
        NotificationService.notify_variant_stock(
            tenant_id=tenant_id,
            item=item,
            variant=variant,
            previous=previous,
            new_stock=variant.stock_quantity,
        )
        return variant
