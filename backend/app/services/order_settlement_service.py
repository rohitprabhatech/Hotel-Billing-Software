"""Settle restaurant orders to bills (BIZ-15)."""

from __future__ import annotations

from decimal import Decimal

from app.constants.orders import ORDER_STATUS_BILLED, ORDER_STATUS_OPEN
from app.constants.payments import (
    DEFAULT_PAYMENT_METHOD,
    PAYMENT_CREDIT,
    normalize_payment_method,
)
from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.bill import Bill, BillItem
from app.repositories.bill_repository import BillRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.bill_service import BillService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.services.order_service import OrderService
from app.utils.exceptions import InsufficientStockError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import calculate_bill_totals, money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class OrderSettlementService:
    @staticmethod
    def settle_order(
        order_id: str,
        *,
        discount=0,
        service_charge=0,
        service_charge_percent=None,
        payment_method: str | None = None,
        customer_id: str | None = None,
        customer_name: str | None = None,
        customer_phone_country_code: str | None = None,
        customer_phone: str | None = None,
        customer_email: str | None = None,
        coupon_code: str | None = None,
        splits: list[dict] | None = None,
    ):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        order = OrderRepository.get_by_id_and_tenant(order_id, ctx.tenant_id)
        if order is None:
            raise NotFoundError("Order not found")
        if order.status != ORDER_STATUS_OPEN:
            raise ValidationError("Only open orders can be settled")
        if not order.items:
            raise ValidationError("Order has no items to settle")

        customer_id = customer_id or order.customer_id
        customer_name = customer_name or order.customer_name
        customer_phone_country_code = customer_phone_country_code or order.customer_phone_country_code
        customer_phone = customer_phone or order.customer_phone_national

        split_specs = OrderSettlementService._normalize_splits(
            order,
            splits=splits,
            payment_method=payment_method,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone_country_code=customer_phone_country_code,
            customer_phone=customer_phone,
            customer_email=customer_email,
        )

        total_service_charge = OrderSettlementService._resolve_service_charge(
            order.items,
            service_charge=service_charge,
            service_charge_percent=service_charge_percent,
        )
        if total_service_charge > 0:
            tenant = TenantRepository.get_by_id(ctx.tenant_id)
            ModuleService.require_enabled(tenant, "service_charge")
        order_subtotal = money(
            sum(money(line.unit_price * line.quantity) for line in order.items)
        )
        manual_discount = money(discount or 0)
        from app.services.coupon_service import CouponService

        coupon, coupon_discount = CouponService.resolve_for_settle(
            code=coupon_code, subtotal=order_subtotal
        )
        total_discount = money(manual_discount + coupon_discount)

        ZERO = money(0)
        allocated_discount = ZERO
        allocated_service = ZERO
        split_payloads = []

        for index, spec in enumerate(split_specs):
            lines = [line for line in order.items if line.id in spec["order_item_ids"]]
            split_subtotal = money(sum(money(line.unit_price * line.quantity) for line in lines))
            if index == len(split_specs) - 1:
                split_discount = money(total_discount - allocated_discount)
                split_service = money(total_service_charge - allocated_service)
            else:
                share = split_subtotal / order_subtotal if order_subtotal > ZERO else ZERO
                split_discount = money(total_discount * share)
                split_service = money(total_service_charge * share)
                allocated_discount = money(allocated_discount + split_discount)
                allocated_service = money(allocated_service + split_service)

            calc_lines = [
                {
                    "item_id": line.item_id,
                    "item_name": line.item_name,
                    "quantity": line.quantity,
                    "unit_price": line.unit_price,
                    "gst_percentage": line.gst_percentage,
                }
                for line in lines
            ]
            try:
                calculated = calculate_bill_totals(calc_lines, split_discount, split_service)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc

            customer_fields = OrderSettlementService._resolve_customer_fields(
                customer_id=spec.get("customer_id"),
                customer_name=spec.get("customer_name"),
                customer_phone_country_code=spec.get("customer_phone_country_code"),
                customer_phone=spec.get("customer_phone"),
                customer_email=spec.get("customer_email"),
            )
            split_payloads.append(
                {
                    "calculated": calculated,
                    "payment_method": spec["payment_method"],
                    "customer_fields": customer_fields,
                }
            )

        from app.services.recipe_stock_service import RecipeStockService

        # Cafe add-on linked inventory (Sprint 6); hotel orders have no add-ons.
        settle_line_ids = {oid for spec in split_specs for oid in spec["order_item_ids"]}
        settle_items = [line for line in order.items if line.id in settle_line_ids]
        merged_stock = RecipeStockService.expand_for_order_settle(ctx.tenant_id, settle_items)
        locked = OrderSettlementService._lock_and_validate_stock(ctx.tenant_id, merged_stock)

        split_group_id = new_uuid() if len(split_payloads) > 1 else None
        reference = order.dining_table.code if order.dining_table else order.order_number
        created_bills = []

        for index, payload in enumerate(split_payloads):
            # Attach coupon metadata to the primary (first) bill only.
            apply_coupon = coupon is not None and index == 0
            bill = OrderSettlementService._create_bill_from_payload(
                ctx=ctx,
                order=order,
                calculated=payload["calculated"],
                payment_method=payload["payment_method"],
                customer_fields=payload["customer_fields"],
                reference=reference,
                split_group_id=split_group_id,
                locked=locked,
                skip_stock=True,
                coupon=coupon if apply_coupon else None,
                coupon_discount=coupon_discount if apply_coupon else money(0),
            )
            created_bills.append(bill)
            if apply_coupon:
                CouponService.redeem(
                    coupon=coupon,
                    bill_id=bill.id,
                    order_id=order.id,
                    discount_applied=coupon_discount,
                    user_id=ctx.user_id,
                )

        OrderSettlementService._deduct_merged_stock(
            locked=locked,
            merged_stock=merged_stock,
            ctx=ctx,
            order=order,
            primary_bill=created_bills[0],
        )

        old_order = OrderService.serialize(order, include_items=True)
        order.status = ORDER_STATUS_BILLED
        order.bill_id = created_bills[0].id
        if order.dining_table_id:
            OrderService._release_table_if_idle(ctx.tenant_id, order.dining_table_id)

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="SETTLE_ORDER",
            entity_type="ORDER",
            entity_id=order.id,
            old_data=old_order,
            new_data={
                **OrderService.serialize(order, include_items=True),
                "bills": [
                    {
                        "id": bill.id,
                        "bill_number": bill.bill_number,
                        "grand_total": float(bill.grand_total),
                        "payment_method": bill.payment_method,
                    }
                    for bill in created_bills
                ],
            },
        )
        db.session.commit()

        return {
            "order": OrderService.serialize(order, include_items=True),
            "bills": [BillService.get_bill(bill.id) for bill in created_bills],
            "split_group_id": split_group_id,
        }

    @staticmethod
    def split_order_bills(
        *,
        order_id: str,
        discount=0,
        service_charge=0,
        service_charge_percent=None,
        splits: list[dict],
    ):
        return OrderSettlementService.settle_order(
            order_id,
            discount=discount,
            service_charge=service_charge,
            service_charge_percent=service_charge_percent,
            splits=splits,
        )

    @staticmethod
    def _normalize_splits(order, *, splits, payment_method, customer_id, **customer_fields):
        if not splits:
            try:
                payment = normalize_payment_method(
                    payment_method if payment_method is not None else DEFAULT_PAYMENT_METHOD
                )
            except ValueError as exc:
                raise ValidationError("Please select a payment method.") from exc
            return [
                {
                    "order_item_ids": {line.id for line in order.items},
                    "payment_method": payment,
                    "customer_id": customer_id,
                    **customer_fields,
                }
            ]

        if len(splits) < 2:
            raise ValidationError("Split settlement requires at least two splits")

        all_ids = set()
        normalized = []
        for row in splits:
            item_ids = {str(i).strip() for i in (row.get("order_item_ids") or []) if str(i).strip()}
            if not item_ids:
                raise ValidationError("Each split must include at least one order line")
            overlap = all_ids & item_ids
            if overlap:
                raise ValidationError("Order lines cannot appear in more than one split")
            all_ids |= item_ids
            try:
                payment = normalize_payment_method(
                    row.get("payment_method") or DEFAULT_PAYMENT_METHOD
                )
            except ValueError as exc:
                raise ValidationError("Please select a payment method for each split.") from exc
            normalized.append(
                {
                    "order_item_ids": item_ids,
                    "payment_method": payment,
                    "customer_id": row.get("customer_id"),
                    "customer_name": row.get("customer_name"),
                    "customer_phone_country_code": row.get("customer_phone_country_code"),
                    "customer_phone": row.get("customer_phone"),
                    "customer_email": row.get("customer_email"),
                }
            )

        order_line_ids = {line.id for line in order.items}
        if all_ids != order_line_ids:
            raise ValidationError("Splits must cover every order line exactly once")

        return normalized

    @staticmethod
    def _resolve_service_charge(items, *, service_charge, service_charge_percent):
        flat = money(service_charge or 0)
        if service_charge_percent not in (None, "", 0, "0"):
            subtotal = money(sum(money(line.unit_price * line.quantity) for line in items))
            percent = money(service_charge_percent)
            if percent < 0:
                raise ValidationError("Service charge percent cannot be negative")
            flat = money(subtotal * percent / Decimal("100"))
        if flat < 0:
            raise ValidationError("Service charge cannot be negative")
        return flat

    @staticmethod
    def _resolve_customer_fields(
        *,
        customer_id,
        customer_name,
        customer_phone_country_code,
        customer_phone,
        customer_email,
    ):
        return OrderService._resolve_customer_fields(
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone_country_code=customer_phone_country_code,
            customer_phone=customer_phone,
        ) | {
            "customer_email": (customer_email or "").strip() or None,
        }

    @staticmethod
    def _lock_and_validate_stock(tenant_id: str, merged: dict[str, Decimal]):
        locked = {}
        for item_id in sorted(merged.keys()):
            item = ItemRepository.lock_by_id_and_tenant(item_id, tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item is inactive or not found: {item_id}")
            locked[item_id] = item

        for item_id, quantity in merged.items():
            item = locked[item_id]
            if item.stock_quantity is None:
                continue
            available = Decimal(item.stock_quantity)
            if quantity > available:
                NotificationService.notify_insufficient_attempt(
                    tenant_id=tenant_id,
                    item_name=item.name,
                    item_id=item.id,
                    available=available,
                    requested=quantity,
                    user_id=require_request_context().user_id,
                )
                db.session.commit()
                raise InsufficientStockError(
                    f"Insufficient stock. Available: {float(available):g}, requested: {float(quantity):g}.",
                    details={
                        "item_id": item.id,
                        "item_name": item.name,
                        "available": float(available),
                        "requested": float(quantity),
                    },
                )
        return locked

    @staticmethod
    def _deduct_merged_stock(*, locked, merged_stock, ctx, order, primary_bill):
        from app.services.notification_service import NotificationService
        from app.services.stock_movement_service import StockMovementService

        for item_id, quantity in merged_stock.items():
            item = locked.get(item_id)
            if item is None or item.stock_quantity is None:
                continue
            parsed_qty = qty(quantity)
            previous = Decimal(item.stock_quantity)
            new_stock = previous - parsed_qty
            item.stock_quantity = new_stock
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="STOCK_DEDUCTED",
                entity_type="ITEM",
                entity_id=item.id,
                old_data={"name": item.name, "stock_quantity": float(previous)},
                new_data={
                    "name": item.name,
                    "stock_quantity": float(new_stock),
                    "quantity": float(parsed_qty),
                    "bill_id": primary_bill.id,
                    "bill_number": primary_bill.bill_number,
                    "order_id": order.id,
                },
            )
            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=-parsed_qty,
                quantity_after=new_stock,
                source="RECIPE",
                reason=f"Recipe consumption (Bill {primary_bill.bill_number}, order {order.order_number})",
                reference_type="BILL",
                reference_id=primary_bill.id,
                created_by=ctx.user_id,
            )
            NotificationService.notify_stock_transition(
                tenant_id=ctx.tenant_id,
                item=item,
                previous=previous,
                new_stock=new_stock,
            )

    @staticmethod
    def _create_bill_from_payload(
        *,
        ctx,
        order,
        calculated,
        payment_method,
        customer_fields,
        reference,
        split_group_id,
        locked,
        skip_stock=False,
        coupon=None,
        coupon_discount=0,
    ):
        if payment_method == PAYMENT_CREDIT and not customer_fields.get("customer_id"):
            raise ValidationError("Customer is required for credit (udhari) bills")

        stock_moves = []
        if not skip_stock:
            for line in calculated["lines"]:
                item = locked.get(line["item_id"])
                if item is None or item.stock_quantity is None:
                    continue
                quantity = qty(line["quantity"])
                previous = Decimal(item.stock_quantity)
                new_stock = previous - quantity
                item.stock_quantity = new_stock
                stock_moves.append((item, previous, new_stock, quantity))

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        sequence, bill_number = BillRepository.allocate_bill_number(
            ctx.tenant_id, tenant.bill_number_prefix if tenant else None
        )

        linked_customer_id = customer_fields.get("customer_id")
        bill = Bill(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            bill_number=bill_number,
            bill_sequence=sequence,
            table_number=reference,
            customer_name=customer_fields.get("customer_name"),
            customer_phone_country_code=customer_fields.get("customer_phone_country_code"),
            customer_phone_national=customer_fields.get("customer_phone_national"),
            customer_phone_e164=customer_fields.get("customer_phone_e164"),
            customer_email=customer_fields.get("customer_email"),
            customer_id=linked_customer_id,
            subtotal=calculated["subtotal"],
            discount=calculated["discount"],
            taxable_amount=calculated["taxable_amount"],
            cgst_amount=calculated["cgst_amount"],
            sgst_amount=calculated["sgst_amount"],
            gst_amount=calculated["gst_amount"],
            service_charge=calculated["service_charge"],
            grand_total=calculated["grand_total"],
            round_off=calculated["round_off"],
            status="FINALIZED",
            payment_method=payment_method,
            created_by=ctx.user_id,
            printed_count=0,
            order_id=order.id,
            split_group_id=split_group_id,
            coupon_id=coupon.id if coupon is not None else None,
            coupon_code=coupon.code if coupon is not None else None,
            coupon_discount=money(coupon_discount or 0),
        )
        BillRepository.add_bill(bill)

        for line in calculated["lines"]:
            BillRepository.add_item(
                BillItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    bill_id=bill.id,
                    item_id=line["item_id"],
                    item_name=line["item_name"],
                    quantity=line["quantity"],
                    unit_price=line["unit_price"],
                    gst_percentage=line["gst_percentage"],
                    discount=line["discount"],
                    taxable_amount=line["taxable_amount"],
                    cgst_amount=line["cgst_amount"],
                    sgst_amount=line["sgst_amount"],
                    total=line["total"],
                )
            )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_BILL",
            entity_type="BILL",
            entity_id=bill.id,
            new_data={
                "bill_number": bill.bill_number,
                "grand_total": float(bill.grand_total),
                "discount": float(bill.discount),
                "service_charge": float(bill.service_charge),
                "status": bill.status,
                "payment_method": bill.payment_method,
                "order_id": order.id,
                "split_group_id": split_group_id,
                "item_count": len(calculated["lines"]),
            },
        )

        from app.services.stock_movement_service import StockMovementService

        for item, previous, new_stock, quantity in stock_moves:
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="STOCK_DEDUCTED",
                entity_type="ITEM",
                entity_id=item.id,
                old_data={"name": item.name, "stock_quantity": float(previous)},
                new_data={
                    "name": item.name,
                    "stock_quantity": float(new_stock),
                    "quantity": float(quantity),
                    "bill_id": bill.id,
                    "bill_number": bill.bill_number,
                    "order_id": order.id,
                },
            )
            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=-quantity,
                quantity_after=new_stock,
                source="RECIPE",
                reason=f"Recipe consumption (Bill {bill.bill_number}, order {order.order_number})",
                reference_type="BILL",
                reference_id=bill.id,
                created_by=ctx.user_id,
            )
            NotificationService.notify_stock_transition(
                tenant_id=ctx.tenant_id,
                item=item,
                previous=previous,
                new_stock=new_stock,
            )

        if payment_method == PAYMENT_CREDIT and linked_customer_id:
            from app.services.party_ledger_service import PartyLedgerService

            PartyLedgerService.record_credit_sale(
                tenant_id=ctx.tenant_id,
                customer_id=linked_customer_id,
                amount=bill.grand_total,
                bill_id=bill.id,
                bill_number=bill.bill_number,
                created_by=ctx.user_id,
            )

        return bill
