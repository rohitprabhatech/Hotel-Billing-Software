"""Hardware / building-material measurement POS and quote (BIZ-35)."""

from decimal import Decimal

from app.constants.measurement import (
    AREA_UOMS,
    LENGTH_UOMS,
    MEASUREMENT_UOMS,
    VOLUME_UOMS,
    WEIGHT_UOMS,
    effective_sale_uom,
    is_measurement_uom,
    measurement_kind,
    qty_step_for_uom,
)
from app.constants.perf import POS_CATALOG_DEFAULT_LIMIT, clamp_pos_catalog_limit
from app.constants.permissions import PERM_BILLING, PERM_ITEMS_READ
from app.constants.uom import UOM_LABELS
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.bulk_pricing_service import BulkPricingService
from app.services.item_service import ItemService
from app.services.module_service import ModuleService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.uom import convert_quantity, stock_quantity_from_sale

MODULE = "uom_measurement"


class HardwarePosService:
    @staticmethod
    def _require_module():
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        return ctx, tenant

    @staticmethod
    def units_catalog():
        require_permission(PERM_ITEMS_READ)
        HardwarePosService._require_module()
        return {
            "units": [
                {
                    "code": code,
                    "label": UOM_LABELS.get(code, code),
                    "kind": measurement_kind(code),
                    "is_measurement": is_measurement_uom(code),
                    "qty_step": float(qty_step_for_uom(code)),
                }
                for code in sorted(UOM_LABELS.keys())
            ],
            "measurement_uoms": sorted(MEASUREMENT_UOMS),
            "length_uoms": sorted(LENGTH_UOMS),
            "weight_uoms": sorted(WEIGHT_UOMS),
            "volume_uoms": sorted(VOLUME_UOMS),
            "area_uoms": sorted(AREA_UOMS),
        }

    @staticmethod
    def pos_catalog(*, q: str | None = None, limit: int = POS_CATALOG_DEFAULT_LIMIT):
        require_permission(PERM_ITEMS_READ)
        ctx, tenant = HardwarePosService._require_module()
        rows, _ = ItemRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            is_active=True,
            page=1,
            per_page=clamp_pos_catalog_limit(limit),
        )
        bulk_enabled = bool(
            tenant and ModuleService.is_enabled_for_tenant(tenant, "bulk_pricing")
        )
        tiers_by_item = {}
        if bulk_enabled and rows:
            tiers_by_item = BulkPricingService.serialize_tiers_for_items(
                ctx.tenant_id, [row.id for row in rows]
            )
        return {
            "items": [
                HardwarePosService._serialize_pos_item(
                    row, price_tiers=tiers_by_item.get(row.id) or []
                )
                for row in rows
            ],
            "scan_defaults": {
                "measurement_uoms": sorted(MEASUREMENT_UOMS),
                "qty_step_measurement": 0.001,
                "qty_step_pcs": 1,
            },
            "bulk_pricing_enabled": bulk_enabled,
        }

    @staticmethod
    def _serialize_pos_item(item, *, price_tiers=None):
        data = ItemService.serialize(item)
        stock_uom = data.get("uom") or "pcs"
        sale_uom = effective_sale_uom(uom=stock_uom, sale_uom=data.get("sale_uom"))
        return {
            "id": data["id"],
            "name": data["name"],
            "barcode": data.get("barcode"),
            "sku": data.get("sku"),
            "brand": data.get("brand"),
            "price": data["price"],
            "gst_percentage": data["gst_percentage"],
            "uom": stock_uom,
            "sale_uom": sale_uom,
            "sale_uom_label": UOM_LABELS.get(sale_uom, sale_uom),
            "measurement_kind": measurement_kind(sale_uom),
            "is_measurement_uom": is_measurement_uom(sale_uom),
            "qty_step": float(qty_step_for_uom(sale_uom)),
            "stock_quantity": data.get("stock_quantity"),
            "category_id": data.get("category_id"),
            "category_name": data.get("category_name"),
            "price_tiers": price_tiers or [],
        }

    @staticmethod
    def quote(*, item_id: str, quantity):
        require_permission(PERM_BILLING)
        ctx, tenant = HardwarePosService._require_module()
        item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
        if item is None or not item.is_active:
            raise NotFoundError("Item not found")
        sale_qty = qty(quantity)
        if sale_qty <= 0:
            raise ValidationError("Quantity must be greater than zero")
        stock_uom = item.uom or "pcs"
        sale_uom = effective_sale_uom(uom=stock_uom, sale_uom=getattr(item, "sale_uom", None))
        stock_qty = stock_quantity_from_sale(
            sale_quantity=sale_qty, stock_uom=stock_uom, sale_uom=sale_uom
        )
        unit_price = BulkPricingService.resolve_many(
            tenant, {item.id: item}, {item.id: sale_qty}
        )[item.id]
        line_total = money(unit_price * sale_qty)
        available = None
        if item.stock_quantity is not None:
            available = float(Decimal(item.stock_quantity))
        return {
            "item_id": item.id,
            "item_name": item.name,
            "quantity": float(sale_qty),
            "sale_uom": sale_uom,
            "sale_uom_label": UOM_LABELS.get(sale_uom, sale_uom),
            "stock_uom": stock_uom,
            "stock_quantity_deducted": float(stock_qty),
            "unit_price": float(unit_price),
            "line_total": float(line_total),
            "gst_percentage": float(item.gst_percentage),
            "stock_available": available,
            "sufficient_stock": available is None or Decimal(str(available)) >= stock_qty,
        }

    @staticmethod
    def convert(*, quantity, from_uom: str, to_uom: str):
        require_permission(PERM_ITEMS_READ)
        HardwarePosService._require_module()
        converted = convert_quantity(quantity, from_uom, to_uom)
        return {
            "quantity": float(qty(quantity)),
            "from_uom": (from_uom or "").strip().lower(),
            "to_uom": (to_uom or "").strip().lower(),
            "converted_quantity": float(converted),
        }
