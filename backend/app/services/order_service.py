"""Restaurant order business logic (BIZ-13)."""

from decimal import Decimal

from app.constants.orders import (
    ORDER_CHANNEL_DELIVERY,
    ORDER_CHANNEL_DINE_IN,
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_OPEN,
    assert_valid_order_channel,
)
from app.constants.permissions import PERM_ORDERS_READ, PERM_ORDERS_WRITE
from app.constants.tables import (
    TABLE_STATUS_AVAILABLE,
    TABLE_STATUS_BILL_PENDING,
    TABLE_STATUS_OCCUPIED,
    TABLE_STATUS_RESERVED,
)
from app.extensions import db
from app.models.cafe_offer import OrderItemAddon
from app.models.order import Order, OrderItem
from app.repositories.dining_table_repository import DiningTableRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.cafe_offer_service import AddonService, ComboService
from app.services.module_service import ModuleService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import calculate_bill_totals, money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive


class OrderService:
    @staticmethod
    def list_orders(*, status=None, channel=None, dining_table_id=None, q=None, page=1, per_page=50):
        require_permission(PERM_ORDERS_READ)
        ctx = require_request_context()
        rows, total = OrderRepository.list_by_tenant(
            ctx.tenant_id,
            status=status,
            channel=channel,
            dining_table_id=dining_table_id,
            q=q,
            page=page,
            per_page=per_page,
        )
        item_counts = OrderRepository.count_items_by_order_ids(
            ctx.tenant_id, [row.id for row in rows]
        )
        return (
            [
                OrderService.serialize(row, include_items=False, item_count=item_counts.get(row.id, 0))
                for row in rows
            ],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_order(order_id: str):
        require_permission(PERM_ORDERS_READ)
        ctx = require_request_context()
        order = OrderRepository.get_by_id_and_tenant(order_id, ctx.tenant_id)
        if order is None:
            raise NotFoundError("Order not found")
        return OrderService.serialize(order, include_items=True)

    @staticmethod
    def create_order(
        *,
        channel: str,
        dining_table_id: str | None = None,
        customer_id: str | None = None,
        customer_name: str | None = None,
        customer_phone_country_code: str | None = None,
        customer_phone: str | None = None,
        delivery_address: str | None = None,
        notes: str | None = None,
        items: list[dict] | None = None,
        combos: list[dict] | None = None,
    ):
        require_permission(PERM_ORDERS_WRITE)
        ctx = require_request_context()
        channel_value = assert_valid_order_channel(channel)

        table = None
        if channel_value == ORDER_CHANNEL_DINE_IN:
            if not dining_table_id:
                raise ValidationError("Dining table is required for dine-in orders")
            table = DiningTableRepository.get_by_id_and_tenant(dining_table_id, ctx.tenant_id)
            if table is None or not table.is_active:
                raise ValidationError("Dining table not found")
            if table.merged_into_id:
                raise ValidationError("Select the primary table, not a merged secondary table")
            existing = OrderRepository.get_open_by_table(ctx.tenant_id, table.id)
            if existing is not None:
                raise ConflictError("This table already has an open order")
            if table.status == TABLE_STATUS_OCCUPIED:
                raise ConflictError("Table is already occupied")
            if table.status == TABLE_STATUS_BILL_PENDING:
                raise ConflictError("Table has a bill pending — settle or reopen the order first")
        elif dining_table_id:
            raise ValidationError("Table can only be set for dine-in orders")

        if channel_value == ORDER_CHANNEL_DELIVERY:
            address = (delivery_address or "").strip()
            if not address:
                raise ValidationError("Delivery address is required for delivery orders")

        customer_fields = OrderService._resolve_customer_fields(
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone_country_code=customer_phone_country_code,
            customer_phone=customer_phone,
        )

        sequence, order_number = OrderRepository.allocate_order_number(ctx.tenant_id)
        order = Order(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            order_number=order_number,
            order_sequence=sequence,
            channel=channel_value,
            status=ORDER_STATUS_OPEN,
            dining_table_id=table.id if table else None,
            customer_id=customer_fields["customer_id"],
            customer_name=customer_fields["customer_name"],
            customer_phone_country_code=customer_fields["customer_phone_country_code"],
            customer_phone_national=customer_fields["customer_phone_national"],
            customer_phone_e164=customer_fields["customer_phone_e164"],
            delivery_address=(delivery_address or "").strip() or None,
            notes=(notes or "").strip() or None,
            created_by=ctx.user_id,
        )
        OrderRepository.add(order)

        if items:
            for row in items:
                addon_ids = row.get("addon_ids") or []
                if addon_ids:
                    OrderService._require_addons_module(ctx.tenant_id)
                OrderService._add_line_to_order(
                    order,
                    row["item_id"],
                    row["quantity"],
                    ctx.tenant_id,
                    addon_ids=addon_ids,
                )
        if combos:
            OrderService._require_addons_module(ctx.tenant_id)
            for row in combos:
                expanded = ComboService.expand_combo_lines(
                    ctx.tenant_id, row["combo_id"], row["quantity"]
                )
                for line in expanded:
                    OrderService._add_line_to_order(
                        order,
                        line["item_id"],
                        line["quantity"],
                        ctx.tenant_id,
                        addon_ids=line.get("addon_ids") or [],
                        combo_id=line.get("combo_id"),
                        unit_price=line.get("unit_price"),
                    )
        OrderService._recalculate_totals(order)

        if table is not None and table.status in {TABLE_STATUS_AVAILABLE, TABLE_STATUS_RESERVED}:
            table.status = TABLE_STATUS_OCCUPIED
            for child in DiningTableRepository.list_merged_children(ctx.tenant_id, table.id):
                child.status = TABLE_STATUS_OCCUPIED

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_ORDER",
            entity_type="ORDER",
            entity_id=order.id,
            new_data=OrderService.serialize(order, include_items=True),
        )
        db.session.commit()
        return OrderService.serialize(order, include_items=True)

    @staticmethod
    def update_order(order_id: str, **fields):
        require_permission(PERM_ORDERS_WRITE)
        ctx = require_request_context()
        order = OrderService._require_open_order(order_id, ctx.tenant_id)
        old = OrderService.serialize(order, include_items=True)

        if fields.get("customer_id_provided") or fields.get("customer_name_provided") or fields.get("customer_phone_provided"):
            customer_fields = OrderService._resolve_customer_fields(
                customer_id=fields.get("customer_id") if fields.get("customer_id_provided") else order.customer_id,
                customer_name=fields.get("customer_name") if fields.get("customer_name_provided") else order.customer_name,
                customer_phone_country_code=(
                    fields.get("customer_phone_country_code")
                    if fields.get("customer_phone_provided")
                    else order.customer_phone_country_code
                ),
                customer_phone=(
                    fields.get("customer_phone")
                    if fields.get("customer_phone_provided")
                    else order.customer_phone_national
                ),
            )
            order.customer_id = customer_fields["customer_id"]
            order.customer_name = customer_fields["customer_name"]
            order.customer_phone_country_code = customer_fields["customer_phone_country_code"]
            order.customer_phone_national = customer_fields["customer_phone_national"]
            order.customer_phone_e164 = customer_fields["customer_phone_e164"]

        if fields.get("delivery_address_provided"):
            if order.channel == ORDER_CHANNEL_DELIVERY and not (fields.get("delivery_address") or "").strip():
                raise ValidationError("Delivery address is required for delivery orders")
            order.delivery_address = (fields.get("delivery_address") or "").strip() or None

        if fields.get("notes_provided"):
            order.notes = (fields.get("notes") or "").strip() or None

        new_data = OrderService.serialize(order, include_items=True)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_ORDER",
            entity_type="ORDER",
            entity_id=order.id,
            old_data=old,
            new_data=new_data,
        )
        db.session.commit()
        return new_data

    @staticmethod
    def add_item(order_id: str, *, item_id: str, quantity, addon_ids: list[str] | None = None):
        require_permission(PERM_ORDERS_WRITE)
        ctx = require_request_context()
        order = OrderService._require_open_order(order_id, ctx.tenant_id)
        parsed_addons = addon_ids or []
        if parsed_addons:
            OrderService._require_addons_module(ctx.tenant_id)
        OrderService._add_line_to_order(
            order,
            item_id,
            quantity,
            ctx.tenant_id,
            addon_ids=parsed_addons,
        )
        OrderService._recalculate_totals(order)
        db.session.commit()
        return OrderService.serialize(order, include_items=True)

    @staticmethod
    def update_item(order_id: str, line_id: str, *, quantity):
        require_permission(PERM_ORDERS_WRITE)
        ctx = require_request_context()
        order = OrderService._require_open_order(order_id, ctx.tenant_id)
        line = OrderRepository.get_item_line(order_id, line_id, ctx.tenant_id)
        if line is None:
            raise NotFoundError("Order line not found")
        parsed_qty = qty(quantity)
        if parsed_qty <= 0:
            raise ValidationError("Quantity must be greater than zero")
        old_qty = float(line.quantity)
        line.quantity = parsed_qty
        OrderService._recalculate_totals(order)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_ORDER_ITEM",
            entity_type="ORDER",
            entity_id=order.id,
            old_data={
                "line_id": line.id,
                "item_name": line.item_name,
                "quantity": old_qty,
                "dining_table_id": order.dining_table_id,
            },
            new_data={
                "line_id": line.id,
                "item_name": line.item_name,
                "quantity": float(parsed_qty),
                "dining_table_id": order.dining_table_id,
            },
        )
        db.session.commit()
        return OrderService.serialize(order, include_items=True)

    @staticmethod
    def remove_item(order_id: str, line_id: str):
        require_permission(PERM_ORDERS_WRITE)
        ctx = require_request_context()
        order = OrderService._require_open_order(order_id, ctx.tenant_id)
        line = OrderRepository.get_item_line(order_id, line_id, ctx.tenant_id)
        if line is None:
            raise NotFoundError("Order line not found")
        db.session.delete(line)
        OrderService._recalculate_totals(order)
        db.session.commit()
        return OrderService.serialize(order, include_items=True)

    @staticmethod
    def cancel_order(order_id: str, *, reason: str | None = None):
        require_permission(PERM_ORDERS_WRITE)
        ctx = require_request_context()
        order = OrderService._require_open_order(order_id, ctx.tenant_id)
        old = OrderService.serialize(order, include_items=True)
        order.status = ORDER_STATUS_CANCELLED
        order.cancelled_by = ctx.user_id
        order.cancelled_at = utc_now_naive()
        order.cancellation_reason = (reason or "").strip() or None

        if order.dining_table_id:
            OrderService._release_table_if_idle(ctx.tenant_id, order.dining_table_id)

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CANCEL_ORDER",
            entity_type="ORDER",
            entity_id=order.id,
            old_data=old,
            new_data=OrderService.serialize(order, include_items=True),
        )
        db.session.commit()
        return OrderService.serialize(order, include_items=True)

    @staticmethod
    def _require_open_order(order_id: str, tenant_id: str) -> Order:
        order = OrderRepository.get_by_id_and_tenant(order_id, tenant_id)
        if order is None:
            raise NotFoundError("Order not found")
        if order.status != ORDER_STATUS_OPEN:
            raise ValidationError("Only open orders can be modified")
        return order

    @staticmethod
    def _require_addons_module(tenant_id: str):
        tenant = TenantRepository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, "addons_combos")

    @staticmethod
    def _line_fingerprint(item_id: str, combo_id: str | None, addon_ids: list[str] | None):
        return (item_id, combo_id or None, tuple(sorted(addon_ids or [])))

    @staticmethod
    def _add_line_to_order(
        order: Order,
        item_id: str,
        quantity,
        tenant_id: str,
        *,
        addon_ids: list[str] | None = None,
        combo_id: str | None = None,
        unit_price=None,
    ):
        parsed_item_id = (item_id or "").strip()
        if not parsed_item_id:
            raise ValidationError("item_id is required")
        parsed_qty = qty(quantity)
        if parsed_qty <= 0:
            raise ValidationError("Quantity must be greater than zero")

        item = ItemRepository.get_by_id_and_tenant(parsed_item_id, tenant_id)
        if item is None or not item.is_active:
            raise ValidationError("Item not found or inactive")

        parsed_addons = list(addon_ids or [])
        fingerprint = OrderService._line_fingerprint(item.id, combo_id, parsed_addons)
        existing = next(
            (
                line
                for line in order.items
                if OrderService._line_fingerprint(
                    line.item_id,
                    line.combo_id,
                    [addon.addon_id for addon in line.addons if addon.addon_id],
                )
                == fingerprint
            ),
            None,
        )
        if existing:
            existing.quantity = qty(existing.quantity + parsed_qty)
            return

        resolved_addons = AddonService.resolve_addons_for_menu_item(
            tenant_id, item.id, parsed_addons
        ) if parsed_addons else []
        addon_extra = sum((addon.extra_price for addon in resolved_addons), Decimal("0"))
        line_unit_price = money(unit_price if unit_price is not None else item.price + addon_extra)

        line = OrderItem(
            id=new_uuid(),
            tenant_id=tenant_id,
            order_id=order.id,
            item_id=item.id,
            item_name=item.name,
            quantity=parsed_qty,
            unit_price=line_unit_price,
            gst_percentage=money(item.gst_percentage),
            line_total=money(Decimal("0")),
            combo_id=combo_id,
        )
        for addon in resolved_addons:
            line.addons.append(
                OrderItemAddon(
                    id=new_uuid(),
                    tenant_id=tenant_id,
                    order_item_id=line.id,
                    addon_id=addon.id,
                    addon_name=addon.name,
                    extra_price=money(addon.extra_price),
                )
            )
        order.items.append(line)

    @staticmethod
    def _recalculate_totals(order: Order):
        if not order.items:
            order.subtotal = money(0)
            order.gst_amount = money(0)
            order.grand_total = money(0)
            return

        calc_lines = [
            {
                "item_id": line.item_id,
                "item_name": line.item_name,
                "quantity": line.quantity,
                "unit_price": line.unit_price,
                "gst_percentage": line.gst_percentage,
            }
            for line in order.items
        ]
        totals = calculate_bill_totals(calc_lines, 0)
        for index, line in enumerate(order.items):
            computed = totals["lines"][index]
            line.line_total = computed["total"]
        order.subtotal = totals["subtotal"]
        order.gst_amount = totals["gst_amount"]
        order.grand_total = totals["grand_total"]

    @staticmethod
    def _release_table_if_idle(tenant_id: str, dining_table_id: str):
        if OrderRepository.get_open_by_table(tenant_id, dining_table_id):
            return
        table = DiningTableRepository.get_by_id_and_tenant(dining_table_id, tenant_id)
        if table is None or not table.is_active:
            return
        table.status = TABLE_STATUS_AVAILABLE
        for child in DiningTableRepository.list_merged_children(tenant_id, table.id):
            child.status = TABLE_STATUS_AVAILABLE

    @staticmethod
    def _resolve_customer_fields(
        *,
        customer_id: str | None,
        customer_name: str | None,
        customer_phone_country_code: str | None,
        customer_phone: str | None,
    ) -> dict:
        linked_customer = None
        if customer_id:
            from app.services.customer_service import CustomerService

            linked_customer = CustomerService.resolve_for_bill(customer_id.strip())

        name_value = (customer_name or "").strip() or None
        phone_cc = (customer_phone_country_code or "").strip() or None
        phone_nat = (customer_phone or "").strip() or None
        phone_e164 = None
        phone_national_store = None
        phone_cc_store = None

        if linked_customer is not None:
            if not name_value:
                name_value = linked_customer.name
            if not phone_cc and not phone_nat and linked_customer.phone_e164:
                phone_cc = linked_customer.phone_country_code
                phone_nat = linked_customer.phone_national

        if phone_cc or phone_nat:
            from app.utils.phone import normalize_phone

            parsed = normalize_phone(country_code=phone_cc, national_number=phone_nat)
            phone_cc_store = parsed["country_code"]
            phone_national_store = parsed["national"]
            phone_e164 = parsed["e164"]

        return {
            "customer_id": linked_customer.id if linked_customer else None,
            "customer_name": name_value,
            "customer_phone_country_code": phone_cc_store,
            "customer_phone_national": phone_national_store,
            "customer_phone_e164": phone_e164,
        }

    @staticmethod
    def serialize(order: Order, *, include_items: bool = True, item_count: int | None = None):
        data = {
            "id": order.id,
            "order_number": order.order_number,
            "order_sequence": order.order_sequence,
            "channel": order.channel,
            "status": order.status,
            "dining_table_id": order.dining_table_id,
            "dining_table_code": order.dining_table.code if order.dining_table else None,
            "customer_id": order.customer_id,
            "customer_name": order.customer_name,
            "customer_phone_country_code": order.customer_phone_country_code,
            "customer_phone_national": order.customer_phone_national,
            "customer_phone_e164": order.customer_phone_e164,
            "delivery_address": order.delivery_address,
            "notes": order.notes,
            "subtotal": float(order.subtotal),
            "gst_amount": float(order.gst_amount),
            "grand_total": float(order.grand_total),
            "bill_id": order.bill_id,
            "created_by": order.created_by,
            "created_by_name": order.creator.name if order.creator else None,
            "cancelled_by": order.cancelled_by,
            "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None,
            "cancellation_reason": order.cancellation_reason,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        }
        if include_items:
            data["items"] = [
                {
                    "id": line.id,
                    "item_id": line.item_id,
                    "item_name": line.item_name,
                    "quantity": float(line.quantity),
                    "unit_price": float(line.unit_price),
                    "gst_percentage": float(line.gst_percentage),
                    "line_total": float(line.line_total),
                    "combo_id": line.combo_id,
                    "addons": [
                        {
                            "id": addon.id,
                            "addon_id": addon.addon_id,
                            "addon_name": addon.addon_name,
                            "extra_price": float(addon.extra_price),
                        }
                        for addon in line.addons
                    ],
                }
                for line in order.items
            ]
        else:
            data["item_count"] = item_count if item_count is not None else len(order.items or [])
        return data
