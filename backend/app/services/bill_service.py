"""Billing finalize and history services."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from flask import current_app

from app.extensions import db
from app.models.bill import Bill, BillItem
from app.models.role import ROLE_BILLING_USER
from app.repositories.bill_repository import BillRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import calculate_bill_totals, money, qty
from app.utils.request_context import require_request_context


class BillService:
    @staticmethod
    def create_bill(*, items: list[dict], discount=0, table_number: str | None = None):
        ctx = require_request_context()
        if not items:
            raise ValidationError("At least one item is required")

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

        calc_lines = []
        for item_id, quantity in merged.items():
            item = ItemRepository.get_by_id_and_tenant(item_id, ctx.tenant_id)
            if item is None or not item.is_active:
                raise ValidationError(f"Item is inactive or not found: {item_id}")
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

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        sequence, bill_number = BillRepository.allocate_bill_number(
            ctx.tenant_id, tenant.bill_number_prefix if tenant else None
        )

        bill = Bill(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            bill_number=bill_number,
            bill_sequence=sequence,
            table_number=(table_number or "").strip() or None,
            subtotal=calculated["subtotal"],
            discount=calculated["discount"],
            taxable_amount=calculated["taxable_amount"],
            cgst_amount=calculated["cgst_amount"],
            sgst_amount=calculated["sgst_amount"],
            gst_amount=calculated["gst_amount"],
            grand_total=calculated["grand_total"],
            round_off=calculated["round_off"],
            status="FINALIZED",
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
                "item_count": len(calculated["lines"]),
            },
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
        return BillService.serialize(bill, include_items=True, include_tenant=True)

    @staticmethod
    def list_bills(*, status=None, page=1, per_page=50, today_only=False, q=None):
        ctx = require_request_context()
        date_from = date_to = None
        if today_only:
            date_from, date_to = BillService._today_bounds()

        bills, total = BillRepository.list_by_tenant(
            ctx.tenant_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            q=q,
            page=page,
            per_page=per_page,
        )
        return (
            [BillService.serialize(b, include_items=False) for b in bills],
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
        bill.status = "CANCELLED"
        bill.cancelled_by = ctx.user_id
        bill.cancelled_at = datetime.now(timezone.utc).replace(tzinfo=None)
        bill.cancellation_reason = reason

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
        total, count = BillRepository.today_sales_total(ctx.tenant_id, day_start, day_end)
        return {
            "total_sales": float(money(total)),
            "bill_count": int(count),
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
    def serialize(bill: Bill, *, include_items=False, include_tenant=False):
        data = {
            "id": bill.id,
            "bill_number": bill.bill_number,
            "bill_sequence": bill.bill_sequence,
            "table_number": bill.table_number,
            "subtotal": float(bill.subtotal),
            "discount": float(bill.discount),
            "taxable_amount": float(bill.taxable_amount),
            "cgst_amount": float(bill.cgst_amount),
            "sgst_amount": float(bill.sgst_amount),
            "gst_amount": float(bill.gst_amount),
            "round_off": float(bill.round_off),
            "grand_total": float(bill.grand_total),
            "status": bill.status,
            "created_by": bill.created_by,
            "created_by_name": bill.creator.name if bill.creator else None,
            "created_at": bill.created_at.isoformat() if bill.created_at else None,
            "printed_count": bill.printed_count,
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
                    "address": tenant.address,
                    "city": tenant.city,
                    "state": tenant.state,
                    "pincode": tenant.pincode,
                    "phone": tenant.phone,
                    "gst_number": tenant.gst_number,
                    "fssai_number": tenant.fssai_number,
                }
        return data
