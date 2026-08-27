"""Kitchen Order Ticket business logic (BIZ-14)."""

from app.constants.kots import (
    ACTIVE_KOT_STATUSES,
    KOT_STATUS_QUEUED,
    KOT_STATUS_READY,
    can_transition_kot_status,
)
from app.constants.orders import ORDER_STATUS_OPEN
from app.constants.permissions import PERM_KOT_READ, PERM_KOT_STATUS, PERM_KOT_WRITE
from app.extensions import db
from app.models.kot import Kot, KotItem
from app.repositories.kot_repository import KotRepository
from app.repositories.order_repository import OrderRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive


class KotService:
    @staticmethod
    def list_kots(*, status=None, order_id=None, page=1, per_page=50):
        require_permission(PERM_KOT_READ)
        ctx = require_request_context()
        rows, total = KotRepository.list_by_tenant(
            ctx.tenant_id,
            status=status,
            order_id=order_id,
            page=page,
            per_page=per_page,
        )
        item_counts = KotRepository.count_items_by_kot_ids(ctx.tenant_id, [row.id for row in rows])
        return (
            [
                KotService.serialize(row, include_items=False, item_count=item_counts.get(row.id, 0))
                for row in rows
            ],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_kitchen_queue():
        require_permission(PERM_KOT_READ)
        ctx = require_request_context()
        rows = KotRepository.list_kitchen_queue(ctx.tenant_id)
        return [KotService.serialize(row, include_items=True) for row in rows]

    @staticmethod
    def get_kot(kot_id: str):
        require_permission(PERM_KOT_READ)
        ctx = require_request_context()
        kot = KotRepository.get_by_id_and_tenant(kot_id, ctx.tenant_id)
        if kot is None:
            raise NotFoundError("KOT not found")
        return KotService.serialize(kot, include_items=True)

    @staticmethod
    def fire_kot_for_order(order_id: str):
        require_permission(PERM_KOT_WRITE)
        ctx = require_request_context()
        order = OrderRepository.get_by_id_and_tenant(order_id, ctx.tenant_id)
        if order is None:
            raise NotFoundError("Order not found")
        if order.status != ORDER_STATUS_OPEN:
            raise ValidationError("KOT can only be fired for open orders")
        if not order.items:
            raise ValidationError("Order has no items to send to kitchen")

        from decimal import Decimal

        from app.utils.money import qty as parse_qty

        sent_qty = KotRepository.sum_sent_qty_by_order_item(ctx.tenant_id, order.id)
        pending_lines: list[tuple] = []
        for line in order.items:
            already = Decimal(str(sent_qty.get(line.id, 0)))
            delta = parse_qty(line.quantity) - already
            if delta > 0:
                pending_lines.append((line, delta))

        if not pending_lines:
            existing = KotRepository.get_latest_by_order(ctx.tenant_id, order.id)
            if existing is None:
                raise ValidationError("Order has no items to send to kitchen")
            old = KotService.serialize(existing, include_items=True)
            existing.print_count = int(existing.print_count or 0) + 1
            existing.printed_at = utc_now_naive()
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="REPRINT_KOT",
                entity_type="KOT",
                entity_id=existing.id,
                old_data=old,
                new_data=KotService.serialize(existing, include_items=True),
            )
            db.session.commit()
            return KotService.serialize(existing, include_items=True)

        sequence, kot_number = KotRepository.allocate_kot_number(ctx.tenant_id)
        now = utc_now_naive()
        kot = Kot(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            kot_number=kot_number,
            kot_sequence=sequence,
            order_id=order.id,
            status=KOT_STATUS_QUEUED,
            channel=order.channel,
            dining_table_id=order.dining_table_id,
            dining_table_code=order.dining_table.code if order.dining_table else None,
            order_number=order.order_number,
            notes=order.notes,
            print_count=1,
            printed_at=now,
            created_by=ctx.user_id,
        )
        for line, delta in pending_lines:
            kot.items.append(
                KotItem(
                    id=new_uuid(),
                    tenant_id=ctx.tenant_id,
                    kot_id=kot.id,
                    order_item_id=line.id,
                    item_id=line.item_id,
                    item_name=line.item_name,
                    quantity=delta,
                )
            )
        KotRepository.add(kot)
        serialized = KotService.serialize(kot, include_items=True)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_KOT",
            entity_type="KOT",
            entity_id=kot.id,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def update_status(kot_id: str, *, status: str):
        require_permission(PERM_KOT_STATUS)
        ctx = require_request_context()
        kot = KotRepository.get_by_id_and_tenant(kot_id, ctx.tenant_id)
        if kot is None:
            raise NotFoundError("KOT not found")
        if kot.status not in ACTIVE_KOT_STATUSES:
            raise ValidationError("This KOT is no longer active on the kitchen board")

        new_status = (status or "").strip().lower()
        if not can_transition_kot_status(kot.status, new_status):
            raise ValidationError(f"Cannot change KOT status from {kot.status} to {new_status}")

        old = KotService.serialize(kot, include_items=True)
        kot.status = new_status
        new_data = KotService.serialize(kot, include_items=True)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_KOT_STATUS",
            entity_type="KOT",
            entity_id=kot.id,
            old_data=old,
            new_data=new_data,
        )
        if new_status == KOT_STATUS_READY:
            from app.services.notification_service import NotificationService

            NotificationService.notify_kot_ready(
                tenant_id=ctx.tenant_id,
                kot_id=kot.id,
                kot_number=kot.kot_number,
                order_number=kot.order_number or "",
                table_code=kot.dining_table_code,
                user_id=ctx.user_id,
            )
        db.session.commit()
        return new_data

    @staticmethod
    def serialize(kot: Kot, *, include_items: bool = True, item_count: int | None = None):
        data = {
            "id": kot.id,
            "kot_number": kot.kot_number,
            "kot_sequence": kot.kot_sequence,
            "order_id": kot.order_id,
            "order_number": kot.order_number,
            "status": kot.status,
            "channel": kot.channel,
            "dining_table_id": kot.dining_table_id,
            "dining_table_code": kot.dining_table_code,
            "notes": kot.notes,
            "print_count": kot.print_count,
            "printed_at": kot.printed_at.isoformat() if kot.printed_at else None,
            "created_by": kot.created_by,
            "created_by_name": kot.creator.name if kot.creator else None,
            "created_at": kot.created_at.isoformat() if kot.created_at else None,
            "updated_at": kot.updated_at.isoformat() if kot.updated_at else None,
        }
        if include_items:
            data["items"] = [
                {
                    "id": line.id,
                    "order_item_id": line.order_item_id,
                    "item_id": line.item_id,
                    "item_name": line.item_name,
                    "quantity": float(line.quantity),
                }
                for line in kot.items
            ]
        else:
            data["item_count"] = item_count if item_count is not None else len(kot.items or [])
        return data
