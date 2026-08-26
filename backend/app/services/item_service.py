"""Item business logic with immutable audit trails."""

from decimal import Decimal, InvalidOperation

from app.constants.permissions import (
    PERM_ITEMS_READ,
    PERM_ITEMS_STOCK,
    PERM_ITEMS_WRITE,
)
from app.constants.uom import DEFAULT_UOM, normalize_uom
from app.extensions import db
from app.models.item import Item
from app.repositories.category_repository import CategoryRepository
from app.repositories.item_repository import ItemRepository
from app.services.audit_service import AuditService
from app.services.category_service import CategoryService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class ItemService:
    @staticmethod
    def list_items(
        *,
        q=None,
        barcode=None,
        isbn=None,
        category_id=None,
        is_active=None,
        stock_status=None,
        page=1,
        per_page=50,
    ):
        require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        status = None
        if stock_status:
            status = str(stock_status).strip().lower()
            if status not in {"low", "out", "tracked"}:
                raise ValidationError("Invalid stock_status filter")
        items, total = ItemRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            barcode=barcode,
            isbn=isbn,
            category_id=category_id,
            is_active=is_active,
            stock_status=status,
            page=page,
            per_page=per_page,
        )
        # One tenant category map avoids N+1 while building hierarchy_path.
        categories = CategoryRepository.list_by_tenant(ctx.tenant_id, active_only=False)
        by_id = {category.id: category for category in categories}
        return (
            [ItemService.serialize(i, category_by_id=by_id) for i in items],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_item(item_id: str):
        require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        return ItemService.serialize(item)

    @staticmethod
    def get_item_by_barcode(barcode: str, *, active_only=True):
        require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        cleaned = (barcode or "").strip()
        if not cleaned:
            raise ValidationError("Barcode is required")
        item = ItemRepository.find_by_tenant_and_barcode(ctx.tenant_id, cleaned)
        matched_variant = None
        matched_serial = None
        if item is None:
            from app.repositories.item_variant_repository import ItemVariantRepository
            from app.repositories.serial_unit_repository import SerialUnitRepository
            from app.repositories.tenant_repository import TenantRepository
            from app.services.module_service import ModuleService
            from app.services.serial_service import SerialService
            from app.models.serial_unit import STATUS_IN_STOCK

            variant = ItemVariantRepository.find_by_barcode(ctx.tenant_id, cleaned)
            if variant is not None and variant.is_active:
                item = ItemRepository.get_by_id_and_tenant(variant.item_id, ctx.tenant_id)
                if item is None:
                    raise NotFoundError("Item not found for barcode")
                matched_variant = variant
            else:
                tenant = TenantRepository.get_by_id(ctx.tenant_id)
                if tenant and ModuleService.is_enabled_for_tenant(tenant, "serial_imei"):
                    try:
                        serial = SerialService.normalize_serial(cleaned)
                    except ValidationError:
                        serial = None
                    unit = (
                        SerialUnitRepository.find_by_serial(ctx.tenant_id, serial)
                        if serial
                        else None
                    )
                    if unit is not None and unit.status == STATUS_IN_STOCK:
                        item = ItemRepository.get_by_id_and_tenant(unit.item_id, ctx.tenant_id)
                        if item is not None:
                            matched_serial = SerialService.serialize(unit, item_name=item.name)
                if item is None:
                    raise NotFoundError("Item not found for barcode")
        if active_only and not item.is_active:
            raise NotFoundError("Item not found for barcode")
        data = ItemService.serialize(item)
        from app.repositories.tenant_repository import TenantRepository
        from app.services.bulk_pricing_service import BulkPricingService
        from app.services.module_service import ModuleService
        from app.services.variant_service import VariantService

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant and ModuleService.is_enabled_for_tenant(tenant, "bulk_pricing"):
            tiers = BulkPricingService.serialize_tiers_for_items(ctx.tenant_id, [item.id])
            data["price_tiers"] = tiers.get(item.id) or []
        else:
            data["price_tiers"] = []
        if matched_variant is not None:
            data["matched_variant"] = VariantService.serialize(
                matched_variant, item_name=item.name
            )
        else:
            data["matched_variant"] = None
        data["matched_serial"] = matched_serial
        return data

    @staticmethod
    def get_item_by_isbn(isbn: str, *, active_only=True):
        require_permission(PERM_ITEMS_READ)
        ctx = require_request_context()
        cleaned = ItemService._normalize_isbn(isbn)
        if not cleaned:
            raise ValidationError("ISBN is required")
        item = ItemRepository.find_by_tenant_and_isbn(ctx.tenant_id, cleaned)
        if item is None:
            raise NotFoundError("Item not found for ISBN")
        if active_only and not item.is_active:
            raise NotFoundError("Item not found for ISBN")
        return ItemService.serialize(item)

    @staticmethod
    def create_item(
        *,
        name,
        category_id,
        description,
        price,
        gst_percentage,
        sku=None,
        barcode=None,
        uom=None,
        sale_uom=None,
        cost_price=None,
        stock_quantity=None,
        minimum_stock_level=None,
        is_menu=False,
        is_veg=None,
        tracks_batches=False,
        block_expired_batches=True,
        tracks_serial=False,
        warranty_months=None,
        brand=None,
        model_name=None,
        isbn=None,
        author=None,
        publisher=None,
        dimension_length=None,
        dimension_width=None,
        dimension_height=None,
        material=None,
        color=None,
    ):
        require_permission(PERM_ITEMS_WRITE)
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

        sku_value = ItemService._normalize_sku(sku)
        if sku_value and ItemRepository.find_by_tenant_and_sku(ctx.tenant_id, sku_value):
            raise ConflictError("Item with this SKU already exists")

        barcode_value = ItemService._normalize_barcode(barcode)
        if barcode_value and ItemRepository.find_by_tenant_and_barcode(ctx.tenant_id, barcode_value):
            raise ConflictError("Item with this barcode already exists")

        isbn_value = ItemService._normalize_isbn(isbn)
        if isbn_value and ItemRepository.find_by_tenant_and_isbn(ctx.tenant_id, isbn_value):
            raise ConflictError("Item with this ISBN already exists")

        uom_value = ItemService._normalize_uom(uom)
        sale_uom_value = ItemService._normalize_optional_uom(sale_uom)

        price_dec = ItemService._parse_money(price, "price")
        cost_dec = ItemService._parse_optional_money(cost_price, "cost_price")
        stock_dec = ItemService._parse_optional_stock(stock_quantity)
        min_stock_dec = ItemService._parse_optional_stock(minimum_stock_level)
        gst_dec = ItemService._parse_gst(gst_percentage)
        tracks_serial_flag = bool(tracks_serial)
        if tracks_serial_flag and bool(tracks_batches):
            raise ValidationError("Serial / IMEI items cannot also track batches")
        if tracks_serial_flag:
            stock_dec = Decimal("0")

        item = Item(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            category_id=category.id,
            created_by=ctx.user_id,
            name=name,
            sku=sku_value,
            barcode=barcode_value,
            uom=uom_value,
            sale_uom=sale_uom_value,
            description=(description or "").strip() or None,
            price=price_dec,
            cost_price=cost_dec,
            gst_percentage=gst_dec,
            stock_quantity=stock_dec,
            minimum_stock_level=min_stock_dec,
            is_active=True,
            is_menu=bool(is_menu),
            is_veg=is_veg if is_veg is None else bool(is_veg),
            tracks_batches=bool(tracks_batches),
            block_expired_batches=True if block_expired_batches is None else bool(block_expired_batches),
            tracks_serial=tracks_serial_flag,
            warranty_months=ItemService._parse_warranty_months(warranty_months),
            brand=ItemService._optional_text(brand, max_len=80),
            model_name=ItemService._optional_text(model_name, max_len=120),
            isbn=isbn_value,
            author=ItemService._optional_text(author, max_len=160),
            publisher=ItemService._optional_text(publisher, max_len=160),
            dimension_length=ItemService._parse_optional_dimension(
                dimension_length, "dimension_length"
            ),
            dimension_width=ItemService._parse_optional_dimension(
                dimension_width, "dimension_width"
            ),
            dimension_height=ItemService._parse_optional_dimension(
                dimension_height, "dimension_height"
            ),
            material=ItemService._optional_text(material, max_len=120),
            color=ItemService._optional_text(color, max_len=80),
        )
        ItemRepository.add(item)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="ITEM_CREATED",
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
        sku=None,
        sku_provided=False,
        barcode=None,
        barcode_provided=False,
        uom=None,
        uom_provided=False,
        sale_uom=None,
        sale_uom_provided=False,
        cost_price=None,
        cost_price_provided=False,
        stock_quantity=None,
        stock_quantity_provided=False,
        minimum_stock_level=None,
        minimum_stock_level_provided=False,
        is_menu=None,
        is_menu_provided=False,
        is_veg=None,
        is_veg_provided=False,
        tracks_batches=None,
        tracks_batches_provided=False,
        block_expired_batches=None,
        block_expired_batches_provided=False,
        tracks_serial=None,
        tracks_serial_provided=False,
        warranty_months=None,
        warranty_months_provided=False,
        brand=None,
        brand_provided=False,
        model_name=None,
        model_name_provided=False,
        isbn=None,
        isbn_provided=False,
        author=None,
        author_provided=False,
        publisher=None,
        publisher_provided=False,
        dimension_length=None,
        dimension_length_provided=False,
        dimension_width=None,
        dimension_width_provided=False,
        dimension_height=None,
        dimension_height_provided=False,
        material=None,
        material_provided=False,
        color=None,
        color_provided=False,
    ):
        require_permission(PERM_ITEMS_WRITE)
        ctx = require_request_context()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")

        old = ItemService.serialize(item)
        price_changed = False
        gst_changed = False
        stock_changed = False
        previous_stock = (
            Decimal(item.stock_quantity) if item.stock_quantity is not None else None
        )

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
            if not category.is_active:
                raise ValidationError("Cannot move item to an inactive category")
            item.category_id = category.id

        if description is not None:
            item.description = description.strip() or None

        if sku_provided:
            sku_value = ItemService._normalize_sku(sku)
            if sku_value:
                existing_sku = ItemRepository.find_by_tenant_and_sku(ctx.tenant_id, sku_value)
                if existing_sku and existing_sku.id != item.id:
                    raise ConflictError("Item with this SKU already exists")
            item.sku = sku_value

        if barcode_provided:
            barcode_value = ItemService._normalize_barcode(barcode)
            if barcode_value:
                existing_barcode = ItemRepository.find_by_tenant_and_barcode(
                    ctx.tenant_id, barcode_value
                )
                if existing_barcode and existing_barcode.id != item.id:
                    raise ConflictError("Item with this barcode already exists")
            item.barcode = barcode_value

        if uom_provided:
            item.uom = ItemService._normalize_uom(uom)
        if sale_uom_provided:
            item.sale_uom = ItemService._normalize_optional_uom(sale_uom)

        if price is not None:
            new_price = ItemService._parse_money(price, "price")
            if Decimal(item.price) != new_price:
                price_changed = True
            item.price = new_price

        if cost_price_provided:
            item.cost_price = ItemService._parse_optional_money(cost_price, "cost_price")

        if gst_percentage is not None:
            new_gst = ItemService._parse_gst(gst_percentage)
            if Decimal(item.gst_percentage) != new_gst:
                gst_changed = True
            item.gst_percentage = new_gst

        if stock_quantity_provided:
            if getattr(item, "tracks_serial", False) or (
                tracks_serial_provided and bool(tracks_serial)
            ):
                raise ValidationError(
                    "Serial / IMEI stock is the count of in-stock units. Receive units instead of setting quantity."
                )
            item.stock_quantity = ItemService._parse_optional_stock(stock_quantity)
            stock_changed = True

        if minimum_stock_level_provided:
            item.minimum_stock_level = ItemService._parse_optional_stock(minimum_stock_level)

        if is_menu_provided:
            item.is_menu = bool(is_menu)

        if is_veg_provided:
            item.is_veg = None if is_veg is None else bool(is_veg)

        if tracks_batches_provided:
            item.tracks_batches = bool(tracks_batches)

        if block_expired_batches_provided:
            item.block_expired_batches = bool(block_expired_batches)

        if tracks_serial_provided:
            if bool(tracks_serial) and getattr(item, "tracks_variants", False):
                raise ValidationError("Variant items cannot also track serial / IMEI units")
            if bool(tracks_serial) and getattr(item, "tracks_batches", False):
                raise ValidationError("Serial / IMEI items cannot also track batches")
            item.tracks_serial = bool(tracks_serial)
            if item.tracks_serial and item.stock_quantity is None:
                item.stock_quantity = Decimal("0")

        if getattr(item, "tracks_serial", False) and getattr(item, "tracks_variants", False):
            raise ValidationError("Variant items cannot also track serial / IMEI units")
        if getattr(item, "tracks_serial", False) and getattr(item, "tracks_batches", False):
            raise ValidationError("Serial / IMEI items cannot also track batches")

        if warranty_months_provided:
            item.warranty_months = ItemService._parse_warranty_months(warranty_months)
        if brand_provided:
            item.brand = ItemService._optional_text(brand, max_len=80)
        if model_name_provided:
            item.model_name = ItemService._optional_text(model_name, max_len=120)
        if isbn_provided:
            isbn_value = ItemService._normalize_isbn(isbn)
            if isbn_value:
                existing_isbn = ItemRepository.find_by_tenant_and_isbn(ctx.tenant_id, isbn_value)
                if existing_isbn and existing_isbn.id != item.id:
                    raise ConflictError("Item with this ISBN already exists")
            item.isbn = isbn_value
        if author_provided:
            item.author = ItemService._optional_text(author, max_len=160)
        if publisher_provided:
            item.publisher = ItemService._optional_text(publisher, max_len=160)
        if dimension_length_provided:
            item.dimension_length = ItemService._parse_optional_dimension(
                dimension_length, "dimension_length"
            )
        if dimension_width_provided:
            item.dimension_width = ItemService._parse_optional_dimension(
                dimension_width, "dimension_width"
            )
        if dimension_height_provided:
            item.dimension_height = ItemService._parse_optional_dimension(
                dimension_height, "dimension_height"
            )
        if material_provided:
            item.material = ItemService._optional_text(material, max_len=120)
        if color_provided:
            item.color = ItemService._optional_text(color, max_len=80)

        new_data = ItemService.serialize(item)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="ITEM_UPDATED",
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
                old_data={"price": old["price"], "name": old["name"]},
                new_data={"price": new_data["price"], "name": new_data["name"]},
            )
        if gst_changed:
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="CHANGE_GST",
                entity_type="ITEM",
                entity_id=item.id,
                old_data={"gst_percentage": old["gst_percentage"], "name": old["name"]},
                new_data={"gst_percentage": new_data["gst_percentage"], "name": new_data["name"]},
            )
        if stock_changed:
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="STOCK_UPDATED",
                entity_type="ITEM",
                entity_id=item.id,
                old_data={"name": old["name"], "stock_quantity": old["stock_quantity"]},
                new_data={"name": new_data["name"], "stock_quantity": new_data["stock_quantity"]},
            )
            new_stock = (
                Decimal(item.stock_quantity) if item.stock_quantity is not None else None
            )
            from app.services.notification_service import NotificationService
            from app.services.stock_movement_service import StockMovementService

            if new_stock is not None and previous_stock != new_stock:
                delta = new_stock if previous_stock is None else (new_stock - previous_stock)
                if delta != 0:
                    StockMovementService.record(
                        tenant_id=ctx.tenant_id,
                        item_id=item.id,
                        delta=delta,
                        quantity_after=new_stock,
                        source="ITEM_UPDATE",
                        reason="Item stock updated",
                        created_by=ctx.user_id,
                    )
            if previous_stock is not None and new_stock is not None:
                NotificationService.notify_stock_transition(
                    tenant_id=ctx.tenant_id,
                    item=item,
                    previous=previous_stock,
                    new_stock=new_stock,
                )

        db.session.commit()
        return new_data

    @staticmethod
    def set_status(item_id: str, is_active: bool, reason: str | None = None):
        require_permission(PERM_ITEMS_WRITE)
        ctx = require_request_context()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")

        old = ItemService.serialize(item)
        desired = bool(is_active)
        if item.is_active == desired:
            return ItemService.serialize(item)

        item.is_active = desired
        action = "ITEM_REACTIVATED" if desired else "ITEM_DEACTIVATED"
        new_data = ItemService.serialize(item)
        if reason and str(reason).strip():
            new_data = {**new_data, "reason": str(reason).strip()}

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action=action,
            entity_type="ITEM",
            entity_id=item.id,
            old_data=old,
            new_data=new_data,
        )
        db.session.commit()
        return ItemService.serialize(item)

    @staticmethod
    def adjust_stock(item_id: str, *, delta, reason: str | None = None):
        """Apply a signed stock delta with row lock (null stock = untracked → reject)."""
        require_permission(PERM_ITEMS_STOCK)
        ctx = require_request_context()
        item = ItemRepository.lock_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")
        if item.stock_quantity is None:
            raise ValidationError(
                "This item does not track stock. Set an initial stock quantity first."
            )

        try:
            change = Decimal(str(delta))
        except Exception as exc:
            raise ValidationError("Invalid stock adjustment amount.") from exc
        if change == 0:
            raise ValidationError("Adjustment amount cannot be zero.")

        from app.services.module_service import ModuleService
        from app.repositories.tenant_repository import TenantRepository

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        reason_text = (reason or "").strip() or None
        if tenant and ModuleService.is_enabled_for_tenant(tenant, "batch_expiry"):
            if not reason_text:
                raise ValidationError("Adjustment reason is required.")

        if getattr(item, "tracks_variants", False):
            raise ValidationError(
                "This item tracks size/color variants. Update stock on the variant matrix."
            )
        if getattr(item, "tracks_serial", False):
            raise ValidationError(
                "This item tracks serial / IMEI units. Receive or sell specific units instead of adjusting quantity."
            )

        previous = Decimal(item.stock_quantity)
        new_stock = previous + change
        if new_stock < 0:
            raise ValidationError(
                f"Insufficient stock. Available: {float(previous):g}, adjustment: {float(change):g}."
            )

        item.stock_quantity = new_stock
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="STOCK_ADJUSTED",
            entity_type="ITEM",
            entity_id=item.id,
            old_data={"name": item.name, "stock_quantity": float(previous)},
            new_data={
                "name": item.name,
                "stock_quantity": float(new_stock),
                "delta": float(change),
                "reason": reason_text,
            },
        )
        from app.services.notification_service import NotificationService
        from app.services.stock_movement_service import StockMovementService

        StockMovementService.record(
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            delta=change,
            quantity_after=new_stock,
            source="ADJUST",
            reason=reason_text,
            created_by=ctx.user_id,
        )
        NotificationService.notify_stock_transition(
            tenant_id=ctx.tenant_id,
            item=item,
            previous=previous,
            new_stock=new_stock,
        )
        db.session.commit()
        return ItemService.serialize(item)

    @staticmethod
    def receive_stock(item_id: str, *, quantity, reason: str | None = None):
        """Add positive stock (or start tracking). Records source RECEIVE."""
        require_permission(PERM_ITEMS_STOCK)
        ctx = require_request_context()
        item = ItemRepository.lock_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None:
            raise NotFoundError("Item not found")

        try:
            qty = Decimal(str(quantity))
        except Exception as exc:
            raise ValidationError("Invalid receive quantity.") from exc
        if qty <= 0:
            raise ValidationError("Receive quantity must be greater than zero.")

        if getattr(item, "tracks_batches", False):
            raise ValidationError(
                "This item tracks batches. Use POST /batches with expiry_date to receive stock."
            )
        if getattr(item, "tracks_variants", False):
            raise ValidationError(
                "This item tracks size/color variants. Update stock on the variant matrix."
            )
        if getattr(item, "tracks_serial", False):
            raise ValidationError(
                "This item tracks serial / IMEI units. Use POST /serial-units to receive stock."
            )

        previous = (
            Decimal(item.stock_quantity) if item.stock_quantity is not None else None
        )
        new_stock = qty if previous is None else (previous + qty)
        item.stock_quantity = new_stock
        reason_text = (reason or "").strip() or None

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="STOCK_RECEIVED",
            entity_type="ITEM",
            entity_id=item.id,
            old_data={
                "name": item.name,
                "stock_quantity": float(previous) if previous is not None else None,
            },
            new_data={
                "name": item.name,
                "stock_quantity": float(new_stock),
                "quantity": float(qty),
                "reason": reason_text,
            },
        )
        from app.services.notification_service import NotificationService
        from app.services.stock_movement_service import StockMovementService

        StockMovementService.record(
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            delta=qty,
            quantity_after=new_stock,
            source="RECEIVE",
            reason=reason_text or "Stock received",
            created_by=ctx.user_id,
        )
        if previous is not None:
            NotificationService.notify_stock_transition(
                tenant_id=ctx.tenant_id,
                item=item,
                previous=previous,
                new_stock=new_stock,
            )
        db.session.commit()
        return ItemService.serialize(item)

    @staticmethod
    def _normalize_sku(value) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @staticmethod
    def _normalize_barcode(value) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @staticmethod
    def _normalize_isbn(value) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip().replace("-", "").replace(" ", "")
        return cleaned or None

    @staticmethod
    def _normalize_uom(value) -> str:
        try:
            return normalize_uom(value, default=DEFAULT_UOM)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    @staticmethod
    def _normalize_optional_uom(value) -> str | None:
        if value is None or str(value).strip() == "":
            return None
        return ItemService._normalize_uom(value)

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
    def _parse_optional_money(value, field_name: str) -> Decimal | None:
        if value is None or value == "":
            return None
        return ItemService._parse_money(value, field_name)

    @staticmethod
    def _parse_optional_stock(value) -> Decimal | None:
        if value is None or value == "":
            return None
        try:
            qty = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError("Invalid stock quantity") from exc
        if qty < 0:
            raise ValidationError("stock_quantity cannot be negative")
        return qty.quantize(Decimal("0.001"))

    @staticmethod
    def _parse_optional_dimension(value, field_name: str) -> Decimal | None:
        if value is None or value == "":
            return None
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError(f"Invalid {field_name}") from exc
        if amount < 0:
            raise ValidationError(f"{field_name} cannot be negative")
        return amount.quantize(Decimal("0.001"))

    @staticmethod
    def _optional_text(value, *, max_len: int) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if len(cleaned) > max_len:
            raise ValidationError(f"Value must be at most {max_len} characters")
        return cleaned

    @staticmethod
    def _parse_warranty_months(value) -> int | None:
        if value is None or value == "":
            return None
        try:
            months = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Invalid warranty months") from exc
        if months < 0 or months > 120:
            raise ValidationError("Warranty months must be between 0 and 120")
        return months if months > 0 else None

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
    def serialize(item: Item, *, category_by_id: dict | None = None):
        category = item.category
        hierarchy_path = None
        if category is not None:
            hierarchy_path = CategoryService._hierarchy_path(
                category, by_id=category_by_id
            )
        return {
            "id": item.id,
            "category_id": item.category_id,
            "category_name": category.name if category else None,
            "category_hierarchy_path": hierarchy_path,
            "name": item.name,
            "sku": item.sku,
            "barcode": item.barcode,
            "uom": item.uom,
            "sale_uom": getattr(item, "sale_uom", None) or item.uom,
            "description": item.description,
            "price": float(item.price),
            "cost_price": float(item.cost_price) if item.cost_price is not None else None,
            "gst_percentage": float(item.gst_percentage),
            "stock_quantity": (
                float(item.stock_quantity) if item.stock_quantity is not None else None
            ),
            "minimum_stock_level": (
                float(item.minimum_stock_level)
                if item.minimum_stock_level is not None
                else None
            ),
            "is_active": item.is_active,
            "is_menu": item.is_menu,
            "is_veg": item.is_veg,
            "tracks_batches": bool(getattr(item, "tracks_batches", False)),
            "block_expired_batches": bool(getattr(item, "block_expired_batches", True)),
            "tracks_variants": bool(getattr(item, "tracks_variants", False)),
            "tracks_serial": bool(getattr(item, "tracks_serial", False)),
            "warranty_months": getattr(item, "warranty_months", None),
            "brand": getattr(item, "brand", None),
            "model_name": getattr(item, "model_name", None),
            "isbn": getattr(item, "isbn", None),
            "author": getattr(item, "author", None),
            "publisher": getattr(item, "publisher", None),
            "dimension_length": (
                float(item.dimension_length)
                if getattr(item, "dimension_length", None) is not None
                else None
            ),
            "dimension_width": (
                float(item.dimension_width)
                if getattr(item, "dimension_width", None) is not None
                else None
            ),
            "dimension_height": (
                float(item.dimension_height)
                if getattr(item, "dimension_height", None) is not None
                else None
            ),
            "material": getattr(item, "material", None),
            "color": getattr(item, "color", None),
            "created_by": item.created_by,
            "created_by_name": item.creator.name if item.creator else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }
