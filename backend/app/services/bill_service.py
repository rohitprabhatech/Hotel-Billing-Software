"""Billing finalize and history services."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from flask import current_app

from app.constants.payments import (
    DEFAULT_PAYMENT_METHOD,
    PAYMENT_CREDIT,
    normalize_payment_method,
    payment_method_label,
)
from app.extensions import db
from app.models.bill import Bill, BillItem
from app.models.role import ROLE_BILLING_USER
from app.repositories.bill_repository import BillRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.utils.exceptions import InsufficientStockError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import calculate_bill_totals, money, qty
from app.utils.request_context import require_request_context


class BillService:
    @staticmethod
    def create_bill(
        *,
        items: list[dict],
        discount=0,
        reference: str | None = None,
        table_number: str | None = None,
        payment_method: str | None = None,
        customer_name: str | None = None,
        customer_phone_country_code: str | None = None,
        customer_phone: str | None = None,
        customer_email: str | None = None,
        customer_id: str | None = None,
    ):
        ctx = require_request_context()
        if not items:
            raise ValidationError("At least one item is required")

        try:
            payment = normalize_payment_method(
                payment_method if payment_method is not None else DEFAULT_PAYMENT_METHOD
            )
        except ValueError as exc:
            raise ValidationError("Please select a payment method.") from exc

        bill_reference = (reference if reference is not None else table_number) or ""
        bill_reference = bill_reference.strip() or None

        customer_name_value = (customer_name or "").strip() or None
        phone_cc = (customer_phone_country_code or "").strip() or None
        phone_nat = (customer_phone or "").strip() or None
        phone_e164 = None
        phone_national_store = None
        phone_cc_store = None

        linked_customer = None
        if customer_id:
            from app.services.customer_service import CustomerService

            linked_customer = CustomerService.resolve_for_bill(customer_id.strip())

        if linked_customer is not None:
            if not customer_name_value and linked_customer.name:
                customer_name_value = linked_customer.name
            if not phone_cc and not phone_nat and linked_customer.phone_e164:
                phone_cc = linked_customer.phone_country_code
                phone_nat = linked_customer.phone_national

        if phone_cc or phone_nat:
            from app.utils.phone import normalize_phone

            parsed = normalize_phone(country_code=phone_cc, national_number=phone_nat)
            phone_cc_store = parsed["country_code"]
            phone_national_store = parsed["national"]
            phone_e164 = parsed["e164"]

        customer_email_store = None
        if customer_email is not None and str(customer_email).strip():
            from app.utils.email_address import normalize_email

            try:
                customer_email_store = normalize_email(customer_email)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc
        elif linked_customer is not None and linked_customer.email:
            customer_email_store = linked_customer.email

        if payment == PAYMENT_CREDIT:
            if linked_customer is None:
                raise ValidationError("Customer is required for credit (udhari) bills")

        # Merge duplicate item_ids from cart
        merged: dict[str, Decimal] = {}
        for row in items:
            item_id = (row.get("item_id") or "").strip()
            if not item_id:
                raise ValidationError("item_id is required for each line")
            try:
                quantity = qty(row.get("quantity"))
            except Exception as exc:
                raise ValidationError("Invalid quantity") from exc
            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero")
            merged[item_id] = merged.get(item_id, Decimal("0")) + quantity

        from app.services.recipe_stock_service import RecipeStockService

        merged = RecipeStockService.expand_for_deduction(ctx.tenant_id, merged)

        # Lock items in stable order, validate all stock, then deduct (atomic with bill).
        locked = {}
        for item_id in sorted(merged.keys()):
            item = ItemRepository.lock_by_id_and_tenant(item_id, ctx.tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item is inactive or not found: {item_id}")
            locked[item_id] = item

        for item_id, quantity in merged.items():
            item = locked[item_id]
            if item.stock_quantity is None:
                continue
            available = Decimal(item.stock_quantity)
            if available <= 0:
                NotificationService.notify_insufficient_attempt(
                    tenant_id=ctx.tenant_id,
                    item_name=item.name,
                    item_id=item.id,
                    available=available,
                    requested=quantity,
                    user_id=ctx.user_id,
                )
                db.session.commit()
                raise InsufficientStockError(
                    f"Item is out of stock: {item.name}",
                    details={
                        "item_id": item.id,
                        "item_name": item.name,
                        "available": float(available),
                        "requested": float(quantity),
                    },
                )
            if quantity > available:
                NotificationService.notify_insufficient_attempt(
                    tenant_id=ctx.tenant_id,
                    item_name=item.name,
                    item_id=item.id,
                    available=available,
                    requested=quantity,
                    user_id=ctx.user_id,
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

        calc_lines = []
        for item_id, quantity in merged.items():
            item = locked[item_id]
            calc_lines.append(
                {
                    "item_id": item.id,
                    "item_name": item.name,
                    "quantity": quantity,
                    "unit_price": item.price,
                    "gst_percentage": item.gst_percentage,
                }
            )

        try:
            calculated = calculate_bill_totals(calc_lines, discount)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        stock_moves = []
        for item_id, quantity in merged.items():
            item = locked[item_id]
            if item.stock_quantity is not None:
                previous = Decimal(item.stock_quantity)
                new_stock = previous - quantity
                item.stock_quantity = new_stock
                stock_moves.append((item, previous, new_stock, quantity))

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        sequence, bill_number = BillRepository.allocate_bill_number(
            ctx.tenant_id, tenant.bill_number_prefix if tenant else None
        )

        bill = Bill(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            bill_number=bill_number,
            bill_sequence=sequence,
            table_number=bill_reference,
            customer_name=customer_name_value,
            customer_phone_country_code=phone_cc_store,
            customer_phone_national=phone_national_store,
            customer_phone_e164=phone_e164,
            customer_email=customer_email_store,
            customer_id=linked_customer.id if linked_customer else None,
            subtotal=calculated["subtotal"],
            discount=calculated["discount"],
            taxable_amount=calculated["taxable_amount"],
            cgst_amount=calculated["cgst_amount"],
            sgst_amount=calculated["sgst_amount"],
            gst_amount=calculated["gst_amount"],
            grand_total=calculated["grand_total"],
            round_off=calculated["round_off"],
            status="FINALIZED",
            payment_method=payment,
            created_by=ctx.user_id,
            printed_count=0,
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
                "status": bill.status,
                "payment_method": bill.payment_method,
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
                old_data={
                    "name": item.name,
                    "stock_quantity": float(previous),
                },
                new_data={
                    "name": item.name,
                    "stock_quantity": float(new_stock),
                    "quantity": float(quantity),
                    "bill_id": bill.id,
                    "bill_number": bill.bill_number,
                },
            )
            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=-quantity,
                quantity_after=new_stock,
                source="BILL",
                reason=f"Bill {bill.bill_number}",
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

        if payment == PAYMENT_CREDIT and linked_customer is not None:
            from app.services.party_ledger_service import PartyLedgerService

            PartyLedgerService.record_credit_sale(
                tenant_id=ctx.tenant_id,
                customer_id=linked_customer.id,
                amount=bill.grand_total,
                bill_id=bill.id,
                bill_number=bill.bill_number,
                created_by=ctx.user_id,
            )

        db.session.commit()
        return BillService.get_bill(bill.id)

    @staticmethod
    def get_bill(bill_id: str):
        ctx = require_request_context()
        bill = BillRepository.get_by_id_and_tenant(bill_id, ctx.tenant_id)
        if bill is None:
            raise NotFoundError("Bill not found")
        if ctx.role == ROLE_BILLING_USER and bill.created_by != ctx.user_id:
            # Billing users can still see today's tenant bills for reprint/ops —
            # keep tenant scoped; allow all tenant bills for counter workflow.
            pass
        from app.repositories.bill_delivery_repository import BillDeliveryRepository
        from app.services.whatsapp_bill_service import WhatsappBillService

        status_map = BillDeliveryRepository.latest_whatsapp_status_map(ctx.tenant_id, [bill.id])
        email_map = BillDeliveryRepository.latest_email_status_map(ctx.tenant_id, [bill.id])
        data = BillService.serialize(
            bill,
            include_items=True,
            include_tenant=True,
            whatsapp_delivery_status=status_map.get(bill.id),
            email_delivery_status=email_map.get(bill.id),
        )
        deliveries = BillDeliveryRepository.list_for_bill(ctx.tenant_id, bill.id)
        data["deliveries"] = [
            WhatsappBillService.serialize_delivery(row) for row in deliveries[:20]
        ]
        return data

    @staticmethod
    def list_bills(
        *,
        status=None,
        page=1,
        per_page=50,
        today_only=False,
        q=None,
        payment_method=None,
        whatsapp_status=None,
        email_status=None,
    ):
        ctx = require_request_context()
        date_from = date_to = None
        if today_only:
            date_from, date_to = BillService._today_bounds()

        method = None
        if payment_method:
            try:
                method = normalize_payment_method(payment_method)
            except ValueError as exc:
                raise ValidationError("Invalid payment method filter") from exc

        wa_status = None
        if whatsapp_status:
            wa_status = str(whatsapp_status).strip().upper()
            if wa_status not in {"PENDING", "SENT", "DELIVERED", "READ", "FAILED"}:
                raise ValidationError("Invalid WhatsApp delivery status filter")

        em_status = None
        if email_status:
            em_status = str(email_status).strip().upper()
            if em_status not in {"PENDING", "SENT", "FAILED"}:
                raise ValidationError("Invalid email delivery status filter")

        bills, total = BillRepository.list_by_tenant(
            ctx.tenant_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            q=q,
            payment_method=method,
            whatsapp_status=wa_status,
            email_status=em_status,
            page=page,
            per_page=per_page,
        )
        from app.repositories.bill_delivery_repository import BillDeliveryRepository

        status_map, email_map = BillDeliveryRepository.latest_delivery_status_maps(
            ctx.tenant_id, [b.id for b in bills]
        )
        return (
            [
                BillService.serialize(
                    b,
                    include_items=False,
                    whatsapp_delivery_status=status_map.get(b.id),
                    email_delivery_status=email_map.get(b.id),
                )
                for b in bills
            ],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def cancel_bill(bill_id: str, reason: str):
        ctx = require_request_context()
        reason = (reason or "").strip()
        if not reason:
            raise ValidationError("Cancellation reason is required")

        bill = BillRepository.get_by_id_and_tenant(bill_id, ctx.tenant_id)
        if bill is None:
            raise NotFoundError("Bill not found")
        if bill.status != "FINALIZED":
            raise ValidationError("Only finalized bills can be cancelled")

        old = BillService.serialize(bill, include_items=False)

        # Restore stock for tracked items (same transaction as cancel).
        line_items = list(bill.items or [])
        restore_ids = sorted({line.item_id for line in line_items if line.item_id})
        from app.services.recipe_stock_service import RecipeStockService

        restore_merged = RecipeStockService.expand_from_lines(ctx.tenant_id, line_items)
        restore_ids = sorted(restore_merged.keys())
        locked = {}
        for item_id in restore_ids:
            item = ItemRepository.lock_by_id_and_tenant(item_id, ctx.tenant_id)
            if item is not None:
                locked[item_id] = item

        from app.services.notification_service import NotificationService
        from app.services.stock_movement_service import StockMovementService

        for item_id, restored_qty in restore_merged.items():
            item = locked.get(item_id)
            if item is None or item.stock_quantity is None:
                continue
            previous = Decimal(item.stock_quantity)
            new_stock = previous + restored_qty
            item.stock_quantity = new_stock
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="STOCK_RESTORED",
                entity_type="ITEM",
                entity_id=item.id,
                old_data={
                    "name": item.name,
                    "stock_quantity": float(previous),
                },
                new_data={
                    "name": item.name,
                    "stock_quantity": float(new_stock),
                    "quantity": float(restored_qty),
                    "bill_id": bill.id,
                    "bill_number": bill.bill_number,
                },
            )
            StockMovementService.record(
                tenant_id=ctx.tenant_id,
                item_id=item.id,
                delta=restored_qty,
                quantity_after=new_stock,
                source="CANCEL",
                reason=f"Cancel bill {bill.bill_number}",
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

        bill.status = "CANCELLED"
        bill.cancelled_by = ctx.user_id
        bill.cancelled_at = datetime.now(timezone.utc).replace(tzinfo=None)
        bill.cancellation_reason = reason

        if bill.payment_method == PAYMENT_CREDIT and bill.customer_id:
            from app.services.party_ledger_service import PartyLedgerService

            PartyLedgerService.record_bill_cancel_reversal(
                tenant_id=ctx.tenant_id,
                customer_id=bill.customer_id,
                amount=bill.grand_total,
                bill_id=bill.id,
                bill_number=bill.bill_number,
                created_by=ctx.user_id,
                reason=reason,
            )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CANCEL_BILL",
            entity_type="BILL",
            entity_id=bill.id,
            old_data=old,
            new_data={
                "bill_number": bill.bill_number,
                "status": bill.status,
                "cancellation_reason": reason,
                "grand_total": float(bill.grand_total),
                "cancelled_by": ctx.user_id,
                "cancelled_by_name": ctx.user_name,
            },
        )
        db.session.commit()
        return BillService.get_bill(bill.id)

    @staticmethod
    def record_print(bill_id: str):
        ctx = require_request_context()
        bill = BillRepository.get_by_id_and_tenant(bill_id, ctx.tenant_id)
        if bill is None:
            raise NotFoundError("Bill not found")

        action = "REPRINT_BILL" if bill.printed_count > 0 else "PRINT_BILL"
        bill.printed_count = int(bill.printed_count or 0) + 1
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action=action,
            entity_type="BILL",
            entity_id=bill.id,
            new_data={
                "bill_number": bill.bill_number,
                "printed_count": bill.printed_count,
                "status": bill.status,
            },
        )
        db.session.commit()
        return {
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "printed_count": bill.printed_count,
            "action": action,
            "bill": BillService.serialize(bill, include_items=True, include_tenant=True),
        }

    @staticmethod
    def today_summary():
        ctx = require_request_context()
        day_start, day_end = BillService._today_bounds()
        summary = BillRepository.today_sales_breakdown(ctx.tenant_id, day_start, day_end)
        return {
            "total_sales": float(money(summary["total_sales"])),
            "bill_count": int(summary["bill_count"]),
            "cash_sales": float(money(summary["cash_sales"])),
            "online_sales": float(money(summary["online_sales"])),
            "cash_bill_count": int(summary["cash_bill_count"]),
            "online_bill_count": int(summary["online_bill_count"]),
        }

    @staticmethod
    def _today_bounds():
        tz_name = current_app.config.get("REPORT_TIMEZONE", "Asia/Kolkata")
        tz = ZoneInfo(tz_name)
        now_local = datetime.now(tz)
        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)
        # Store naive UTC-equivalent for SQLite/MySQL DATETIME without tz
        start = start_local.astimezone(timezone.utc).replace(tzinfo=None)
        end = end_local.astimezone(timezone.utc).replace(tzinfo=None)
        return start, end

    @staticmethod
    def serialize(
        bill: Bill,
        *,
        include_items=False,
        include_tenant=False,
        whatsapp_delivery_status=None,
        email_delivery_status=None,
    ):
        from app.utils.email_address import mask_email
        from app.utils.phone import mask_e164

        data = {
            "id": bill.id,
            "bill_number": bill.bill_number,
            "bill_sequence": bill.bill_sequence,
            "reference": bill.table_number,
            "table_number": bill.table_number,  # legacy alias
            "customer_name": bill.customer_name,
            "customer_phone_country_code": bill.customer_phone_country_code,
            "customer_phone_national": bill.customer_phone_national,
            "customer_phone_masked": mask_e164(bill.customer_phone_e164),
            "customer_email": bill.customer_email,
            "customer_email_masked": mask_email(bill.customer_email),
            "customer_id": bill.customer_id,
            "subtotal": float(bill.subtotal),
            "discount": float(bill.discount),
            "taxable_amount": float(bill.taxable_amount),
            "cgst_amount": float(bill.cgst_amount),
            "sgst_amount": float(bill.sgst_amount),
            "gst_amount": float(bill.gst_amount),
            "service_charge": float(getattr(bill, "service_charge", 0) or 0),
            "round_off": float(bill.round_off),
            "grand_total": float(bill.grand_total),
            "status": bill.status,
            "payment_method": bill.payment_method or DEFAULT_PAYMENT_METHOD,
            "payment_method_label": payment_method_label(bill.payment_method),
            "order_id": getattr(bill, "order_id", None),
            "split_group_id": getattr(bill, "split_group_id", None),
            "created_by": bill.created_by,
            "created_by_name": bill.creator.name if bill.creator else None,
            "created_at": bill.created_at.isoformat() if bill.created_at else None,
            "printed_count": bill.printed_count,
            "whatsapp_delivery_status": whatsapp_delivery_status,
            "email_delivery_status": email_delivery_status,
            "cancellation_reason": bill.cancellation_reason,
            "cancelled_by": bill.cancelled_by,
            "cancelled_at": bill.cancelled_at.isoformat() if bill.cancelled_at else None,
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
                    "discount": float(line.discount),
                    "taxable_amount": float(line.taxable_amount),
                    "cgst_amount": float(line.cgst_amount),
                    "sgst_amount": float(line.sgst_amount),
                    "total": float(line.total),
                }
                for line in (bill.items or [])
            ]
        if include_tenant:
            tenant = TenantRepository.get_by_id(bill.tenant_id)
            if tenant:
                data["tenant"] = {
                    "business_name": tenant.business_name,
                    "business_type": tenant.business_type,
                    "address": tenant.address,
                    "city": tenant.city,
                    "state": tenant.state,
                    "pincode": tenant.pincode,
                    "phone": tenant.phone,
                    "gst_number": tenant.gst_number,
                    "fssai_number": tenant.fssai_number,
                }
        return data
