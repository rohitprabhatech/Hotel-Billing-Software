"""Sales returns and size/color exchanges (BIZ-27).

GST/refund kept simple: refund is proportional to the original bill line total.
"""

from decimal import Decimal

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.role import ROLE_BILLING_USER
from app.models.sales_return import KIND_EXCHANGE, KIND_RETURN, SalesReturn, SalesReturnItem
from app.repositories.bill_repository import BillRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.item_variant_repository import ItemVariantRepository
from app.repositories.sales_return_repository import SalesReturnRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.stock_movement_service import StockMovementService
from app.services.variant_service import VariantService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class SalesReturnService:
    MODULE = "returns_exchange"

    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, SalesReturnService.MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can process returns and exchanges")
        return ctx

    @staticmethod
    def serialize(row: SalesReturn) -> dict:
        bill = row.bill
        return {
            "id": row.id,
            "return_number": row.return_number,
            "kind": row.kind,
            "reason": row.reason,
            "refund_amount": float(row.refund_amount),
            "extra_payable": float(row.extra_payable),
            "status": row.status,
            "bill_id": row.bill_id,
            "bill_number": bill.bill_number if bill else None,
            "created_by": row.created_by,
            "created_by_name": row.creator.name if row.creator else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "items": [
                {
                    "id": line.id,
                    "bill_item_id": line.bill_item_id,
                    "item_id": line.item_id,
                    "variant_id": line.variant_id,
                    "item_name": line.item_name,
                    "quantity": float(line.quantity),
                    "line_refund": float(line.line_refund),
                    "exchange_item_id": line.exchange_item_id,
                    "exchange_variant_id": line.exchange_variant_id,
                    "exchange_item_name": line.exchange_item_name,
                    "serial_unit_id": line.serial_unit_id,
                    "exchange_serial_unit_id": line.exchange_serial_unit_id,
                    "quarantine": bool(line.quarantine),
                }
                for line in (row.items or [])
            ],
        }

    @staticmethod
    def lookup_bill(bill_number: str | None = None, bill_id: str | None = None):
        ctx = SalesReturnService._require(write=False)
        bill = None
        if bill_id:
            bill = BillRepository.get_by_id_and_tenant(bill_id.strip(), ctx.tenant_id)
        elif bill_number:
            bill = BillRepository.get_by_number_and_tenant(bill_number.strip(), ctx.tenant_id)
        if bill is None:
            raise NotFoundError("Bill not found")
        if bill.status != "FINALIZED":
            raise ValidationError("Only finalized bills can be returned or exchanged")

        already = SalesReturnRepository.returned_qty_by_bill_item(ctx.tenant_id, bill.id)
        lines = []
        for line in bill.items or []:
            sold = qty(line.quantity)
            used = qty(already.get(line.id, 0))
            remaining = sold - used
            if remaining < 0:
                remaining = qty(0)
            unit_refund = money(Decimal(line.total) / sold) if sold > 0 else money(0)
            lines.append(
                {
                    "bill_item_id": line.id,
                    "item_id": line.item_id,
                    "variant_id": getattr(line, "variant_id", None),
                    "item_name": line.item_name,
                    "quantity_sold": float(sold),
                    "quantity_returned": float(used),
                    "quantity_returnable": float(remaining),
                    "unit_price": float(line.unit_price),
                    "unit_refund": float(unit_refund),
                    "line_total": float(line.total),
                    "serial_unit_id": getattr(line, "serial_unit_id", None),
                    "serial_number": getattr(line, "serial_number", None),
                    "is_serial": bool(getattr(line, "serial_unit_id", None)),
                }
            )
        return {
            "bill_id": bill.id,
            "bill_number": bill.bill_number,
            "grand_total": float(bill.grand_total),
            "status": bill.status,
            "customer_name": bill.customer_name,
            "items": lines,
        }

    @staticmethod
    def list_returns(*, bill_id=None, page=1, per_page=50):
        ctx = SalesReturnService._require(write=False)
        rows, total = SalesReturnRepository.list_for_tenant(
            ctx.tenant_id, bill_id=bill_id, page=page, per_page=per_page
        )
        return (
            [SalesReturnService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_return(return_id: str):
        ctx = SalesReturnService._require(write=False)
        row = SalesReturnRepository.get_by_id(ctx.tenant_id, return_id)
        if row is None:
            raise NotFoundError("Return not found")
        return SalesReturnService.serialize(row)

    @staticmethod
    def _restock(ctx, item, variant_id, quantity, *, source: str, reference_id: str, reason: str):
        if item is None:
            return
        previous = Decimal(item.stock_quantity or 0)
        if variant_id:
            VariantService.restore(ctx.tenant_id, item, variant_id, quantity)
        elif item.stock_quantity is not None:
            item.stock_quantity = qty(previous + quantity)
        StockMovementService.record(
            tenant_id=ctx.tenant_id,
            item_id=item.id,
            delta=quantity,
            quantity_after=Decimal(item.stock_quantity or 0),
            source=source,
            reason=reason,
            reference_type="RETURN",
            reference_id=reference_id,
            created_by=ctx.user_id,
        )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="STOCK_RESTORED",
            entity_type="ITEM",
            entity_id=item.id,
            old_data={"name": item.name, "stock_quantity": float(previous)},
            new_data={
                "name": item.name,
                "stock_quantity": float(item.stock_quantity or 0),
                "quantity": float(quantity),
                "variant_id": variant_id,
                "source": source,
            },
        )

    @staticmethod
    def create(*, bill_id, kind, reason, items):
        ctx = SalesReturnService._require(write=True)
        kind = (kind or KIND_RETURN).upper()
        reason_text = (reason or "").strip()
        if not reason_text:
            raise ValidationError("Reason is required")

        bill = BillRepository.get_by_id_and_tenant(bill_id.strip(), ctx.tenant_id)
        if bill is None:
            raise NotFoundError("Bill not found")
        if bill.status != "FINALIZED":
            raise ValidationError("Only finalized bills can be returned or exchanged")

        already = SalesReturnRepository.returned_qty_by_bill_item(ctx.tenant_id, bill.id)
        lines_by_id = {line.id: line for line in (bill.items or [])}

        prepared = []
        refund_total = money(0)
        extra_total = money(0)
        for row in items or []:
            bill_item = lines_by_id.get((row.get("bill_item_id") or "").strip())
            if bill_item is None:
                raise ValidationError("Return line does not belong to this bill")
            quantity = qty(row.get("quantity"))
            if quantity <= 0:
                raise ValidationError("Return quantity must be greater than zero")
            remaining = qty(bill_item.quantity) - qty(already.get(bill_item.id, 0))
            if quantity > remaining:
                raise ValidationError(
                    f"Cannot return more than remaining quantity for {bill_item.item_name} "
                    f"(returnable {float(remaining):g})"
                )
            already[bill_item.id] = float(qty(already.get(bill_item.id, 0)) + quantity)
            unit_refund = money(Decimal(bill_item.total) / qty(bill_item.quantity))
            line_refund = money(unit_refund * quantity)
            exchange_item_id = (row.get("exchange_item_id") or "").strip() or None
            exchange_variant_id = (row.get("exchange_variant_id") or "").strip() or None
            exchange_serial_unit_id = (row.get("exchange_serial_unit_id") or "").strip() or None
            quarantine = bool(row.get("quarantine"))
            serial_unit_id = getattr(bill_item, "serial_unit_id", None)
            is_serial = bool(serial_unit_id)
            if is_serial and quantity != Decimal("1.000"):
                raise ValidationError("Serialized lines must be returned one unit at a time")
            exchange_item = None
            exchange_name = None
            exchange_value = money(0)
            if kind == KIND_EXCHANGE:
                if is_serial:
                    if not exchange_serial_unit_id:
                        raise ValidationError("Select the replacement serial / IMEI for exchange")
                    if exchange_item_id or exchange_variant_id:
                        raise ValidationError("Use exchange serial for serialized product exchange")
                    exchange_item = ItemRepository.lock_by_id_and_tenant(bill_item.item_id, ctx.tenant_id)
                    if exchange_item is None or not exchange_item.is_active:
                        raise ValidationError("Exchange item is inactive or not found")
                    if exchange_serial_unit_id == serial_unit_id:
                        raise ValidationError("Exchange serial must be different from the returned one")
                    exchange_name = bill_item.item_name
                    exchange_value = money(Decimal(exchange_item.price) * quantity)
                else:
                    if not exchange_item_id:
                        raise ValidationError("Select the size/color to give in exchange")
                    exchange_item = ItemRepository.lock_by_id_and_tenant(exchange_item_id, ctx.tenant_id)
                    if exchange_item is None or not exchange_item.is_active:
                        raise ValidationError("Exchange item is inactive or not found")
                    if VariantService.item_tracks_variants(exchange_item):
                        if not exchange_variant_id:
                            raise ValidationError(f"Select a size/color for {exchange_item.name}")
                        if exchange_variant_id == (bill_item.variant_id or ""):
                            raise ValidationError("Exchange variant must be different from the returned one")
                    elif exchange_variant_id:
                        raise ValidationError(f"{exchange_item.name} has no size/color variants")
                    exchange_name = exchange_item.name
                    if exchange_variant_id:
                        variant = ItemVariantRepository.get_by_id(ctx.tenant_id, exchange_variant_id)
                        if variant:
                            exchange_name = f"{exchange_item.name} ({variant.size}/{variant.color})"
                    exchange_value = money(Decimal(exchange_item.price) * quantity)
                extra_total = money(extra_total + max(money(0), exchange_value - line_refund))
                refund_total = money(refund_total + max(money(0), line_refund - exchange_value))
            else:
                if exchange_item_id or exchange_variant_id or exchange_serial_unit_id:
                    raise ValidationError("Exchange target is only valid for exchanges")
                refund_total = money(refund_total + line_refund)
            prepared.append(
                {
                    "bill_item": bill_item,
                    "quantity": quantity,
                    "line_refund": line_refund,
                    "exchange_item": exchange_item,
                    "exchange_item_id": exchange_item_id or (exchange_item.id if exchange_item else None),
                    "exchange_variant_id": exchange_variant_id,
                    "exchange_item_name": exchange_name,
                    "exchange_serial_unit_id": exchange_serial_unit_id,
                    "serial_unit_id": serial_unit_id,
                    "quarantine": quarantine,
                    "is_serial": is_serial,
                }
            )

        sequence, return_number = SalesReturnRepository.allocate_number(ctx.tenant_id)
        header = SalesReturn(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            bill_id=bill.id,
            return_number=return_number,
            return_sequence=sequence,
            kind=kind,
            reason=reason_text,
            refund_amount=refund_total,
            extra_payable=extra_total if kind == KIND_EXCHANGE else money(0),
            status="FINALIZED",
            created_by=ctx.user_id,
        )
        SalesReturnRepository.add(header)
        db.session.flush()

        source = "EXCHANGE" if kind == KIND_EXCHANGE else "RETURN"
        from app.services.serial_service import SerialService

        for payload in prepared:
            bill_item = payload["bill_item"]
            item = None
            if bill_item.item_id:
                item = ItemRepository.lock_by_id_and_tenant(bill_item.item_id, ctx.tenant_id)
            if payload["is_serial"] and payload["serial_unit_id"]:
                if kind == KIND_EXCHANGE and payload["exchange_serial_unit_id"]:
                    new_unit = SerialService.exchange_unit(
                        ctx.tenant_id,
                        old_unit_id=payload["serial_unit_id"],
                        new_unit_id=payload["exchange_serial_unit_id"],
                        bill_id=bill.id,
                        bill_item_id=bill_item.id,
                        user_id=ctx.user_id,
                    )
                    bill_item.serial_unit_id = new_unit.id
                    bill_item.serial_number = new_unit.serial
                    if item:
                        bill_item.item_name = f"{item.name} · {new_unit.serial}"
                else:
                    SerialService.return_from_sale(
                        ctx.tenant_id,
                        payload["serial_unit_id"],
                        quarantine=payload["quarantine"],
                        user_id=ctx.user_id,
                        bill_id=bill.id,
                    )
            else:
                SalesReturnService._restock(
                    ctx,
                    item,
                    getattr(bill_item, "variant_id", None),
                    payload["quantity"],
                    source=source,
                    reference_id=header.id,
                    reason=f"{kind} {return_number} for bill {bill.bill_number}",
                )
            if (
                kind == KIND_EXCHANGE
                and payload["exchange_item"] is not None
                and not payload["is_serial"]
            ):
                outgoing = payload["exchange_item"]
                prev_out = Decimal(outgoing.stock_quantity or 0)
                if VariantService.item_tracks_variants(outgoing):
                    VariantService.deduct(
                        ctx.tenant_id,
                        outgoing,
                        payload["exchange_variant_id"],
                        payload["quantity"],
                        user_id=ctx.user_id,
                    )
                elif outgoing.stock_quantity is not None:
                    available = Decimal(outgoing.stock_quantity)
                    if payload["quantity"] > available:
                        raise ValidationError(
                            f"Insufficient stock for exchange item {outgoing.name}"
                        )
                    outgoing.stock_quantity = qty(available - payload["quantity"])
                StockMovementService.record(
                    tenant_id=ctx.tenant_id,
                    item_id=outgoing.id,
                    delta=-payload["quantity"],
                    quantity_after=Decimal(outgoing.stock_quantity or 0),
                    source=source,
                    reason=f"{kind} {return_number} for bill {bill.bill_number}",
                    reference_type="RETURN",
                    reference_id=header.id,
                    created_by=ctx.user_id,
                )
                AuditService.log(
                    tenant_id=ctx.tenant_id,
                    action="STOCK_DEDUCTED",
                    entity_type="ITEM",
                    entity_id=outgoing.id,
                    old_data={"name": outgoing.name, "stock_quantity": float(prev_out)},
                    new_data={
                        "name": outgoing.name,
                        "stock_quantity": float(outgoing.stock_quantity or 0),
                        "quantity": float(payload["quantity"]),
                        "variant_id": payload["exchange_variant_id"],
                        "source": source,
                    },
                )
            SalesReturnRepository.add_item(
                SalesReturnItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    return_id=header.id,
                    bill_item_id=bill_item.id,
                    item_id=bill_item.item_id,
                    variant_id=getattr(bill_item, "variant_id", None),
                    item_name=bill_item.item_name,
                    quantity=payload["quantity"],
                    line_refund=payload["line_refund"],
                    exchange_item_id=payload["exchange_item_id"],
                    exchange_variant_id=payload["exchange_variant_id"],
                    exchange_item_name=payload["exchange_item_name"],
                    serial_unit_id=payload.get("serial_unit_id"),
                    exchange_serial_unit_id=payload.get("exchange_serial_unit_id"),
                    quarantine=bool(payload.get("quarantine")),
                )
            )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_RETURN" if kind == KIND_RETURN else "CREATE_EXCHANGE",
            entity_type="SALES_RETURN",
            entity_id=header.id,
            new_data={
                "return_number": return_number,
                "bill_id": bill.id,
                "bill_number": bill.bill_number,
                "kind": kind,
                "refund_amount": float(header.refund_amount),
                "extra_payable": float(header.extra_payable),
                "reason": reason_text,
            },
        )
        db.session.commit()
        db.session.refresh(header)
        return SalesReturnService.serialize(header)
