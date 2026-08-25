"""Serial / IMEI unit stock (BIZ-29). Shared by mobile and electronics."""

from sqlalchemy.exc import IntegrityError

from app.constants.permissions import PERM_ITEMS_READ, PERM_ITEMS_STOCK
from app.extensions import db
from app.models.serial_unit import STATUS_IN_STOCK, STATUS_SOLD, SerialUnit
from app.repositories.item_repository import ItemRepository
from app.repositories.serial_unit_repository import SerialUnitRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.stock_movement_service import StockMovementService
from app.utils.exceptions import ConflictError, InsufficientStockError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive

MODULE = "serial_imei"


class SerialService:
    @staticmethod
    def _require_module():
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        return ctx, tenant

    @staticmethod
    def item_tracks_serial(item) -> bool:
        return bool(getattr(item, "tracks_serial", False))

    @staticmethod
    def normalize_serial(value: str | None) -> str:
        cleaned = "".join((value or "").split()).upper()
        if len(cleaned) < 4 or len(cleaned) > 64:
            raise ValidationError("Serial / IMEI must be 4–64 characters")
        if not all(ch.isalnum() for ch in cleaned):
            raise ValidationError("Serial / IMEI may contain only letters and digits")
        return cleaned

    @staticmethod
    def serialize(unit: SerialUnit, *, item_name: str | None = None) -> dict:
        return {
            "id": unit.id,
            "item_id": unit.item_id,
            "item_name": item_name or (unit.item.name if unit.item else None),
            "serial": unit.serial,
            "status": unit.status,
            "sold_bill_id": unit.sold_bill_id,
            "sold_bill_item_id": unit.sold_bill_item_id,
            "sold_at": unit.sold_at.isoformat() if unit.sold_at else None,
            "received_at": unit.received_at.isoformat() if unit.received_at else None,
            "created_at": unit.created_at.isoformat() if unit.created_at else None,
        }

    @staticmethod
    def sync_item_stock(item) -> None:
        count = SerialUnitRepository.count_in_stock(item.tenant_id, item.id)
        item.stock_quantity = count
        item.tracks_serial = True

    @staticmethod
    def list_units(*, item_id=None, status=None, q=None, page=1, per_page=50):
        require_permission(PERM_ITEMS_READ)
        ctx, _ = SerialService._require_module()
        rows, total = SerialUnitRepository.list_for_tenant(
            ctx.tenant_id,
            item_id=item_id,
            status=status,
            q=q,
            page=page,
            per_page=per_page,
        )
        return (
            [SerialService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_by_serial(serial: str):
        require_permission(PERM_ITEMS_READ)
        ctx, _ = SerialService._require_module()
        try:
            cleaned = SerialService.normalize_serial(serial)
        except ValidationError as exc:
            raise NotFoundError("Serial unit not found") from exc
        unit = SerialUnitRepository.find_by_serial(ctx.tenant_id, cleaned)
        if unit is None:
            raise NotFoundError("Serial unit not found")
        return SerialService.serialize(unit)

    @staticmethod
    def receive(*, item_id: str, serial: str):
        require_permission(PERM_ITEMS_STOCK)
        ctx, _ = SerialService._require_module()
        item = ItemRepository.lock_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None or not item.is_active:
            raise NotFoundError("Item not found")
        if getattr(item, "tracks_variants", False):
            raise ValidationError("Variant items cannot also track serial / IMEI units")
        cleaned = SerialService.normalize_serial(serial)
        existing = SerialUnitRepository.find_by_serial(ctx.tenant_id, cleaned)
        if existing is not None:
            raise ConflictError("This serial / IMEI is already registered")

        unit = SerialUnit(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            serial=cleaned,
            status=STATUS_IN_STOCK,
            received_at=utc_now_naive(),
        )
        SerialUnitRepository.add(unit)
        item.tracks_serial = True
        SerialService.sync_item_stock(item)
        try:
            db.session.flush()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictError("This serial / IMEI is already registered") from exc

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="RECEIVE_SERIAL",
            entity_type="SERIAL_UNIT",
            entity_id=unit.id,
            new_data={"serial": cleaned, "item_id": item.id, "item_name": item.name},
        )
        StockMovementService.record(
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            delta=1,
            quantity_after=item.stock_quantity,
            source="RECEIVE",
            reason=f"Receive serial {cleaned}",
            reference_type="SERIAL_UNIT",
            reference_id=unit.id,
            created_by=ctx.user_id,
        )
        db.session.commit()
        return SerialService.serialize(unit, item_name=item.name)

    @staticmethod
    def allocate_for_sale(tenant_id: str, item, *, serial_unit_id=None, serial=None, user_id=None):
        """Mark one in-stock unit sold. Caller holds the item row lock."""
        unit = None
        if serial_unit_id:
            unit = SerialUnitRepository.lock_by_id(tenant_id, serial_unit_id)
        elif serial:
            unit = SerialUnitRepository.lock_by_serial(
                tenant_id, SerialService.normalize_serial(serial)
            )
        if unit is None:
            raise ValidationError(f"Select an in-stock serial / IMEI for {item.name}")
        if unit.item_id != item.id:
            raise ValidationError("Serial / IMEI does not belong to this item")
        if unit.status != STATUS_IN_STOCK:
            raise InsufficientStockError(
                f"Serial / IMEI {unit.serial} is not available for sale",
                details={"serial": unit.serial, "status": unit.status},
            )
        unit.status = STATUS_SOLD
        unit.sold_at = utc_now_naive()
        SerialService.sync_item_stock(item)
        AuditService.log(
            tenant_id=tenant_id,
            action="SELL_SERIAL",
            entity_type="SERIAL_UNIT",
            entity_id=unit.id,
            user_id=user_id,
            old_data={"status": STATUS_IN_STOCK, "serial": unit.serial},
            new_data={"status": STATUS_SOLD, "serial": unit.serial, "item_id": item.id},
        )
        return unit

    @staticmethod
    def bind_sold_line(unit: SerialUnit, *, bill_id: str, bill_item_id: str) -> None:
        unit.sold_bill_id = bill_id
        unit.sold_bill_item_id = bill_item_id

    @staticmethod
    def restore(tenant_id: str, item, serial_unit_id: str, *, bill_id: str | None = None):
        unit = SerialUnitRepository.lock_by_id(tenant_id, serial_unit_id)
        if unit is None:
            return
        if unit.status != STATUS_SOLD:
            return
        if bill_id and unit.sold_bill_id and unit.sold_bill_id != bill_id:
            return
        unit.status = STATUS_IN_STOCK
        unit.sold_bill_id = None
        unit.sold_bill_item_id = None
        unit.sold_at = None
        SerialService.sync_item_stock(item)
        AuditService.log(
            tenant_id=tenant_id,
            action="RESTORE_SERIAL",
            entity_type="SERIAL_UNIT",
            entity_id=unit.id,
            old_data={"status": STATUS_SOLD, "serial": unit.serial},
            new_data={"status": STATUS_IN_STOCK, "serial": unit.serial},
        )
