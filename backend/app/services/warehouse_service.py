"""Warehouse CRUD, balances, and stock transfers (BIZ-38 / BIZ-53)."""

from collections import defaultdict
from decimal import Decimal

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK
from app.extensions import db
from app.models.role import ROLE_BILLING_USER
from app.models.warehouse import (
    TRANSFER_COMPLETED,
    StockTransfer,
    StockTransferItem,
    Warehouse,
    WarehouseStock,
)
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.warehouse_repository import StockTransferRepository, WarehouseRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.services.stock_movement_service import StockMovementService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "warehouse"


class WarehouseService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_ITEMS_STOCK if write else PERM_ITEMS_READ)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage warehouses")
        return ctx, tenant

    @staticmethod
    def module_enabled(tenant) -> bool:
        return bool(tenant and ModuleService.is_enabled_for_tenant(tenant, MODULE))

    @staticmethod
    def ensure_default_warehouse(tenant_id: str) -> Warehouse:
        """Create MAIN default and seed balances from items.stock_quantity if needed."""
        existing = WarehouseRepository.get_default(tenant_id)
        if existing is not None:
            return existing
        any_wh = WarehouseRepository.list_for_tenant(tenant_id, active_only=False)
        if any_wh:
            # Promote first warehouse if none marked default.
            row = any_wh[0]
            WarehouseRepository.clear_default(tenant_id)
            row.is_default = True
            row.is_active = True
            db.session.flush()
            return row

        warehouse = Warehouse(
            id=new_uuid(),
            tenant_id=tenant_id,
            code="MAIN",
            name="Main warehouse",
            is_default=True,
            is_active=True,
        )
        WarehouseRepository.add(warehouse)
        db.session.flush()

        # Seed from current item stock (tracked items only).
        from app.models.item import Item

        items = Item.query.filter(
            Item.tenant_id == tenant_id,
            Item.stock_quantity.isnot(None),
        ).all()
        seeded = 0
        for item in items:
            amount = qty(item.stock_quantity)
            if amount == 0:
                continue
            WarehouseRepository.add_stock(
                WarehouseStock(
                    id=new_uuid(),
                    tenant_id=tenant_id,
                    warehouse_id=warehouse.id,
                    item_id=item.id,
                    quantity=amount,
                )
            )
            seeded += 1
        db.session.flush()
        AuditService.log(
            tenant_id=tenant_id,
            action="CREATE_WAREHOUSE",
            entity_type="WAREHOUSE",
            entity_id=warehouse.id,
            new_data={
                **WarehouseService.serialize_warehouse(warehouse),
                "auto_default": True,
                "seeded_stock_rows": seeded,
            },
        )
        return warehouse

    @staticmethod
    def serialize_warehouse(row: Warehouse) -> dict:
        return {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "address": row.address,
            "notes": row.notes,
            "is_default": bool(row.is_default),
            "is_active": bool(row.is_active),
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def serialize_stock(row: WarehouseStock) -> dict:
        return {
            "id": row.id,
            "warehouse_id": row.warehouse_id,
            "warehouse_code": row.warehouse.code if row.warehouse else None,
            "warehouse_name": row.warehouse.name if row.warehouse else None,
            "item_id": row.item_id,
            "item_name": row.item.name if row.item else None,
            "quantity": float(row.quantity),
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def serialize_transfer(row: StockTransfer) -> dict:
        return {
            "id": row.id,
            "transfer_number": row.transfer_number,
            "status": row.status,
            "from_warehouse_id": row.from_warehouse_id,
            "from_warehouse_name": row.from_warehouse.name if row.from_warehouse else None,
            "to_warehouse_id": row.to_warehouse_id,
            "to_warehouse_name": row.to_warehouse.name if row.to_warehouse else None,
            "notes": row.notes,
            "created_by": row.created_by,
            "created_by_name": row.creator.name if row.creator else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "items": [
                {
                    "id": line.id,
                    "item_id": line.item_id,
                    "item_name": line.item_name,
                    "quantity": float(line.quantity),
                }
                for line in (row.items or [])
            ],
        }

    @staticmethod
    def list_warehouses(*, include_inactive: bool = False):
        ctx, _ = WarehouseService._require(write=False)
        WarehouseService.ensure_default_warehouse(ctx.tenant_id)
        rows = WarehouseRepository.list_for_tenant(
            ctx.tenant_id, active_only=not include_inactive
        )
        return [WarehouseService.serialize_warehouse(row) for row in rows]

    @staticmethod
    def create_warehouse(*, code: str, name: str, address=None, notes=None, is_default=False):
        ctx, _ = WarehouseService._require(write=True)
        WarehouseService.ensure_default_warehouse(ctx.tenant_id)
        code_value = (code or "").strip().upper()
        name_value = (name or "").strip()
        if not code_value or not name_value:
            raise ValidationError("Warehouse code and name are required")
        if WarehouseRepository.get_by_code(ctx.tenant_id, code_value):
            raise ValidationError("Warehouse code already exists")
        if is_default:
            WarehouseRepository.clear_default(ctx.tenant_id)
        row = Warehouse(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            code=code_value,
            name=name_value,
            address=(address or "").strip() or None,
            notes=(notes or "").strip() or None,
            is_default=bool(is_default),
            is_active=True,
        )
        WarehouseRepository.add(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_WAREHOUSE",
            entity_type="WAREHOUSE",
            entity_id=row.id,
            new_data={"code": code_value, "name": name_value, "is_default": bool(is_default)},
        )
        db.session.commit()
        return WarehouseService.serialize_warehouse(row)

    @staticmethod
    def update_warehouse(
        warehouse_id: str,
        *,
        name=None,
        address=None,
        notes=None,
        is_active=None,
        is_default=None,
    ):
        ctx, _ = WarehouseService._require(write=True)
        row = WarehouseRepository.get_by_id(ctx.tenant_id, warehouse_id)
        if row is None:
            raise NotFoundError("Warehouse not found")
        old = WarehouseService.serialize_warehouse(row)
        if name is not None:
            name_value = (name or "").strip()
            if not name_value:
                raise ValidationError("Name is required")
            row.name = name_value
        if address is not None:
            row.address = (address or "").strip() or None
        if notes is not None:
            row.notes = (notes or "").strip() or None
        if is_active is not None:
            if row.is_default and not bool(is_active):
                raise ValidationError("Cannot deactivate the default warehouse")
            row.is_active = bool(is_active)
        if is_default is True:
            WarehouseRepository.clear_default(ctx.tenant_id)
            row.is_default = True
            row.is_active = True
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_WAREHOUSE",
            entity_type="WAREHOUSE",
            entity_id=row.id,
            old_data=old,
            new_data=WarehouseService.serialize_warehouse(row),
        )
        db.session.commit()
        return WarehouseService.serialize_warehouse(row)

    @staticmethod
    def list_stocks(*, warehouse_id=None, item_id=None, page=1, per_page=100):
        ctx, _ = WarehouseService._require(write=False)
        WarehouseService.ensure_default_warehouse(ctx.tenant_id)
        rows, total = WarehouseRepository.list_stocks(
            ctx.tenant_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            page=page,
            per_page=per_page,
        )
        return (
            [WarehouseService.serialize_stock(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def _get_or_create_stock(tenant_id: str, warehouse_id: str, item_id: str) -> WarehouseStock:
        row = WarehouseRepository.lock_stock(tenant_id, warehouse_id, item_id)
        if row is not None:
            return row
        row = WarehouseStock(
            id=new_uuid(),
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            quantity=Decimal("0"),
        )
        WarehouseRepository.add_stock(row)
        db.session.flush()
        return WarehouseRepository.lock_stock(tenant_id, warehouse_id, item_id)

    @staticmethod
    def adjust_warehouse_stock(
        *,
        tenant_id: str,
        warehouse_id: str,
        item_id: str,
        delta: Decimal,
        allow_negative: bool = False,
        notify: bool = False,
        item=None,
        warehouse=None,
    ) -> Decimal:
        """Adjust warehouse balance; returns new quantity. Does not touch item.stock_quantity."""
        stock = WarehouseService._get_or_create_stock(tenant_id, warehouse_id, item_id)
        current = qty(stock.quantity)
        new_qty = qty(current + delta)
        if not allow_negative and new_qty < 0:
            raise ValidationError(
                f"Insufficient warehouse stock. Available: {float(current):g}, "
                f"requested: {float(abs(delta)):g}."
            )
        stock.quantity = new_qty
        db.session.flush()
        if notify and delta != 0:
            if item is None:
                item = ItemRepository.get_by_id_and_tenant(item_id, tenant_id)
            if warehouse is None:
                warehouse = WarehouseRepository.get_by_id(tenant_id, warehouse_id)
            if item is not None and warehouse is not None:
                NotificationService.notify_warehouse_stock_transition(
                    tenant_id=tenant_id,
                    item=item,
                    warehouse=warehouse,
                    stock_id=stock.id,
                    previous=current,
                    new_stock=new_qty,
                )
        return new_qty

    @staticmethod
    def deduct_for_sale(
        *,
        tenant_id: str,
        warehouse_id: str | None,
        item_id: str,
        quantity: Decimal,
    ) -> str:
        """Deduct from warehouse for a sale. Returns warehouse_id used."""
        warehouse = None
        if warehouse_id:
            warehouse = WarehouseRepository.get_by_id(tenant_id, warehouse_id)
            if warehouse is None or not warehouse.is_active:
                raise ValidationError("Warehouse not found or inactive")
        else:
            warehouse = WarehouseService.ensure_default_warehouse(tenant_id)
        item = ItemRepository.get_by_id_and_tenant(item_id, tenant_id)
        need = qty(quantity)
        stock = WarehouseRepository.get_stock(tenant_id, warehouse.id, item_id)
        current = qty(stock.quantity) if stock else Decimal("0")
        # Legacy tenants may have item.stock_quantity without mirrored warehouse rows.
        if current < need and item is not None and item.stock_quantity is not None:
            pre_sale_item = qty(item.stock_quantity) + need
            if pre_sale_item >= need:
                bootstrap = pre_sale_item - current
                if bootstrap > 0:
                    WarehouseService.adjust_warehouse_stock(
                        tenant_id=tenant_id,
                        warehouse_id=warehouse.id,
                        item_id=item_id,
                        delta=bootstrap,
                        item=item,
                        warehouse=warehouse,
                    )
        WarehouseService.adjust_warehouse_stock(
            tenant_id=tenant_id,
            warehouse_id=warehouse.id,
            item_id=item_id,
            delta=-need,
            notify=True,
            item=item,
            warehouse=warehouse,
        )
        return warehouse.id

    @staticmethod
    def restore_for_cancel(
        *,
        tenant_id: str,
        warehouse_id: str | None,
        item_id: str,
        quantity: Decimal,
    ) -> None:
        if not warehouse_id:
            warehouse = WarehouseRepository.get_default(tenant_id)
            warehouse_id = warehouse.id if warehouse else None
        if not warehouse_id:
            return
        WarehouseService.adjust_warehouse_stock(
            tenant_id=tenant_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            delta=qty(quantity),
        )

    @staticmethod
    def receive_into_default(*, tenant_id: str, item_id: str, quantity: Decimal) -> None:
        warehouse = WarehouseService.ensure_default_warehouse(tenant_id)
        WarehouseService.adjust_warehouse_stock(
            tenant_id=tenant_id,
            warehouse_id=warehouse.id,
            item_id=item_id,
            delta=qty(quantity),
        )

    @staticmethod
    def create_transfer(
        *,
        from_warehouse_id: str,
        to_warehouse_id: str,
        items: list[dict],
        notes=None,
    ):
        ctx, _ = WarehouseService._require(write=True)
        WarehouseService.ensure_default_warehouse(ctx.tenant_id)
        if from_warehouse_id == to_warehouse_id:
            raise ValidationError("From and to warehouses must differ")
        source = WarehouseRepository.get_by_id(ctx.tenant_id, from_warehouse_id)
        target = WarehouseRepository.get_by_id(ctx.tenant_id, to_warehouse_id)
        if source is None or not source.is_active:
            raise ValidationError("Source warehouse not found or inactive")
        if target is None or not target.is_active:
            raise ValidationError("Destination warehouse not found or inactive")
        if not items:
            raise ValidationError("At least one line item is required")

        resolved = []
        for raw in items:
            item_id = (raw.get("item_id") or "").strip()
            if not item_id:
                raise ValidationError("item_id is required")
            item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item not found: {item_id}")
            if item.stock_quantity is None:
                raise ValidationError(f"{item.name} does not track stock")
            quantity = qty(raw.get("quantity"))
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero")
            resolved.append({"item": item, "quantity": quantity})

        # Pre-validate all source balances before mutating any row (BIZ-53).
        needed: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        item_by_id = {}
        for line in resolved:
            needed[line["item"].id] += line["quantity"]
            item_by_id[line["item"].id] = line["item"]
        for item_id, need in needed.items():
            stock = WarehouseRepository.get_stock(ctx.tenant_id, source.id, item_id)
            available = qty(stock.quantity) if stock else Decimal("0")
            if available < need:
                name = item_by_id[item_id].name
                raise ValidationError(
                    f"Insufficient stock at {source.code} for {name}. "
                    f"Available: {float(available):g}, requested: {float(need):g}."
                )

        sequence, number = StockTransferRepository.allocate_number(ctx.tenant_id)
        transfer = StockTransfer(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            transfer_number=number,
            transfer_sequence=sequence,
            from_warehouse_id=source.id,
            to_warehouse_id=target.id,
            status=TRANSFER_COMPLETED,
            notes=(notes or "").strip() or None,
            created_by=ctx.user_id,
        )
        StockTransferRepository.add(transfer)
        db.session.flush()

        for line in resolved:
            item = line["item"]
            quantity = line["quantity"]
            WarehouseService.adjust_warehouse_stock(
                tenant_id=ctx.tenant_id,
                warehouse_id=source.id,
                item_id=item.id,
                delta=-quantity,
                notify=True,
                item=item,
                warehouse=source,
            )
            WarehouseService.adjust_warehouse_stock(
                tenant_id=ctx.tenant_id,
                warehouse_id=target.id,
                item_id=item.id,
                delta=quantity,
                notify=True,
                item=item,
                warehouse=target,
            )
            # Item-level total unchanged; ledger still records the movement pair.
            after = qty(item.stock_quantity or 0)
            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=-quantity,
                quantity_after=after,
                source="TRANSFER_OUT",
                reason=f"Transfer {number} → {target.code}",
                reference_type="STOCK_TRANSFER",
                reference_id=transfer.id,
                created_by=ctx.user_id,
            )
            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=quantity,
                quantity_after=after,
                source="TRANSFER_IN",
                reason=f"Transfer {number} ← {source.code}",
                reference_type="STOCK_TRANSFER",
                reference_id=transfer.id,
                created_by=ctx.user_id,
            )
            db.session.add(
                StockTransferItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    transfer_id=transfer.id,
                    item_id=item.id,
                    item_name=item.name,
                    quantity=quantity,
                )
            )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_STOCK_TRANSFER",
            entity_type="STOCK_TRANSFER",
            entity_id=transfer.id,
            new_data={
                "transfer_number": number,
                "from": source.code,
                "to": target.code,
                "lines": len(resolved),
            },
        )
        db.session.commit()
        return WarehouseService.serialize_transfer(
            StockTransferRepository.get_by_id(ctx.tenant_id, transfer.id)
        )

    @staticmethod
    def list_transfers(*, page=1, per_page=50):
        ctx, _ = WarehouseService._require(write=False)
        rows, total = StockTransferRepository.list_for_tenant(
            ctx.tenant_id, page=page, per_page=per_page
        )
        return (
            [WarehouseService.serialize_transfer(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_transfer(transfer_id: str):
        ctx, _ = WarehouseService._require(write=False)
        row = StockTransferRepository.get_by_id(ctx.tenant_id, transfer_id)
        if row is None:
            raise NotFoundError("Stock transfer not found")
        return WarehouseService.serialize_transfer(row)
