"""Shared custom product orders with advances (BIZ-42 bakery; BIZ-48 furniture)."""

from datetime import datetime
from decimal import Decimal

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.custom_order import (
    ALLOWED_CUSTOM_ORDER_STATUSES,
    ALLOWED_ORDER_TYPES,
    ORDER_TYPE_BAKERY,
    ORDER_TYPE_FURNITURE,
    STATUS_BOOKED,
    STATUS_CANCELLED,
    STATUS_DELIVERED,
    STATUS_READY,
    STATUS_TRANSITIONS,
    CustomOrderPayment,
    CustomProductOrder,
)
from app.models.role import ROLE_BILLING_USER
from app.repositories.custom_order_repository import CustomOrderRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import ZERO, money, qty
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context
from app.utils.tokens import utc_now_naive

MODULE = "custom_orders"


class CustomOrderService:
    @staticmethod
    def _require(*, write: bool, manage: bool = False):
        """write=create/advance; manage=status (owner/manager only)."""
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if manage and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can update custom order status")
        return ctx, tenant

    @staticmethod
    def serialize(order: CustomProductOrder) -> dict:
        total = money(order.total_amount)
        advance = money(order.advance_paid)
        remaining = money(total - advance)
        if remaining < ZERO:
            remaining = ZERO
        payment_rows = (
            CustomOrderPayment.query.filter_by(
                tenant_id=order.tenant_id, custom_order_id=order.id
            )
            .order_by(CustomOrderPayment.created_at.asc())
            .all()
        )
        return {
            "id": order.id,
            "order_number": order.order_number,
            "order_type": order.order_type,
            "customer_id": order.customer_id,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "title": order.title,
            "size": order.size,
            "flavor": order.flavor,
            "quantity": float(order.quantity),
            "total_amount": float(total),
            "advance_paid": float(advance),
            "remaining_amount": float(remaining),
            "delivery_at": order.delivery_at.isoformat() if order.delivery_at else None,
            "status": order.status,
            "notes": order.notes,
            "bill_id": order.bill_id,
            "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
            "created_by": order.created_by,
            "created_by_name": order.creator.name if order.creator else None,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "payments": [
                {
                    "id": pay.id,
                    "amount": float(pay.amount),
                    "payment_method": pay.payment_method,
                    "notes": pay.notes,
                    "created_by": pay.created_by,
                    "created_at": pay.created_at.isoformat() if pay.created_at else None,
                }
                for pay in payment_rows
            ],
        }

    @staticmethod
    def list_orders(*, order_type=None, status=None, page=1, per_page=100):
        CustomOrderService._require(write=False)
        ctx = require_request_context()
        rows, total = CustomOrderRepository.list_for_tenant(
            ctx.tenant_id,
            order_type=order_type,
            status=status,
            page=page,
            per_page=per_page,
        )
        return (
            [CustomOrderService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 100), 1), 200),
                "total": total,
            },
        )

    @staticmethod
    def get_order(order_id: str):
        ctx, _ = CustomOrderService._require(write=False)
        row = CustomOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if row is None:
            raise NotFoundError("Custom order not found")
        return CustomOrderService.serialize(row)

    @staticmethod
    def create(
        *,
        order_type: str = ORDER_TYPE_BAKERY,
        customer_id=None,
        customer_name=None,
        customer_phone=None,
        title: str,
        size=None,
        flavor=None,
        quantity=1,
        total_amount,
        advance_amount=0,
        payment_method: str = "cash",
        delivery_at=None,
        notes=None,
    ):
        ctx, _ = CustomOrderService._require(write=True)
        type_key = (order_type or ORDER_TYPE_BAKERY).strip().lower()
        if type_key not in ALLOWED_ORDER_TYPES:
            raise ValidationError("Invalid order_type")
        title_text = (title or "").strip()
        if not title_text:
            raise ValidationError("title is required")

        total = money(total_amount)
        if total <= ZERO:
            raise ValidationError("total_amount must be greater than zero")
        advance = money(advance_amount or 0)
        if advance < ZERO:
            raise ValidationError("advance_amount cannot be negative")
        if advance >= total:
            raise ValidationError("Advance must be less than total amount")

        qty_val = qty(quantity or 1)
        if qty_val <= 0:
            raise ValidationError("quantity must be greater than zero")

        cust_id = (customer_id or "").strip() or None
        name = (customer_name or "").strip() or None
        phone = (customer_phone or "").strip() or None
        if cust_id:
            customer = CustomerRepository.get_by_id_and_tenant(cust_id, ctx.tenant_id)
            if customer is None:
                raise ValidationError("Customer not found")
            name = name or customer.name
            phone = phone or getattr(customer, "phone", None)

        delivery = delivery_at
        if isinstance(delivery, str):
            try:
                delivery = datetime.fromisoformat(delivery.replace("Z", ""))
            except ValueError as exc:
                raise ValidationError("delivery_at must be an ISO datetime") from exc

        order_id = new_uuid()
        _, order_number = CustomOrderRepository.allocate_number(ctx.tenant_id)
        order = CustomProductOrder(
            id=order_id,
            tenant_id=ctx.tenant_id,
            order_number=order_number,
            order_type=type_key,
            customer_id=cust_id,
            customer_name=name,
            customer_phone=phone,
            title=title_text,
            size=(size or "").strip() or None,
            flavor=(flavor or "").strip() or None,
            quantity=qty_val,
            total_amount=total,
            advance_paid=ZERO,
            delivery_at=delivery,
            status=STATUS_BOOKED,
            notes=(notes or "").strip() or None,
            created_by=ctx.user_id,
        )
        CustomOrderRepository.add(order)

        if advance > ZERO:
            CustomOrderService._add_payment(
                order,
                amount=advance,
                payment_method=payment_method,
                notes="Initial advance",
                user_id=ctx.user_id,
                require_partial=True,
            )

        db.session.flush()
        order = CustomOrderRepository.get_by_id(ctx.tenant_id, order_id)
        serialized = CustomOrderService.serialize(order)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_CUSTOM_ORDER",
            entity_type="CUSTOM_ORDER",
            entity_id=order.id,
            new_data=serialized,
        )
        db.session.commit()

        if delivery is not None:
            NotificationService.notify_custom_order_delivery(
                tenant_id=ctx.tenant_id,
                order_number=order_number,
                title=title_text,
                delivery_at=delivery.isoformat(),
                user_id=ctx.user_id,
            )
        return serialized

    @staticmethod
    def _add_payment(
        order: CustomProductOrder,
        *,
        amount: Decimal,
        payment_method,
        notes,
        user_id,
        require_partial: bool = False,
    ):
        pay_amount = money(amount)
        if pay_amount <= ZERO:
            raise ValidationError("Payment amount must be greater than zero")
        remaining = money(order.total_amount) - money(order.advance_paid)
        if pay_amount > remaining:
            raise ValidationError(
                f"Advance exceeds remaining balance. Remaining: {float(remaining):.2f}."
            )
        if require_partial and pay_amount >= money(order.total_amount):
            raise ValidationError("Advance must be less than total amount")

        payment = CustomOrderPayment(
            id=new_uuid(),
            tenant_id=order.tenant_id,
            custom_order_id=order.id,
            amount=pay_amount,
            payment_method=(payment_method or "cash").strip().lower() or "cash",
            notes=(notes or "").strip() or None,
            created_by=user_id,
        )
        CustomOrderRepository.add_payment(payment)
        order.advance_paid = money(order.advance_paid) + pay_amount
        db.session.flush()
        return payment

    @staticmethod
    def record_advance(*, order_id: str, amount, payment_method="cash", notes=None):
        ctx, _ = CustomOrderService._require(write=True)
        order = CustomOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if order is None:
            raise NotFoundError("Custom order not found")
        if order.status in (STATUS_CANCELLED, STATUS_DELIVERED):
            raise ValidationError("Cannot record advance on a cancelled or delivered order")

        old = CustomOrderService.serialize(order)
        CustomOrderService._add_payment(
            order,
            amount=amount,
            payment_method=payment_method,
            notes=notes,
            user_id=ctx.user_id,
            require_partial=False,
        )
        db.session.flush()
        db.session.expire(order, ["payments"])
        order = CustomOrderRepository.get_by_id(ctx.tenant_id, order_id)
        serialized = CustomOrderService.serialize(order)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CUSTOM_ORDER_ADVANCE",
            entity_type="CUSTOM_ORDER",
            entity_id=order.id,
            old_data=old,
            new_data=serialized,
        )
        db.session.commit()
        return serialized

    @staticmethod
    def update_status(order_id: str, *, status: str, notes=None):
        ctx, tenant = CustomOrderService._require(write=True, manage=True)
        order = CustomOrderRepository.get_by_id(ctx.tenant_id, order_id)
        if order is None:
            raise NotFoundError("Custom order not found")

        new_status = (status or "").strip().upper()
        if new_status not in ALLOWED_CUSTOM_ORDER_STATUSES:
            raise ValidationError("Invalid status")
        allowed = STATUS_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            raise ValidationError(f"Cannot move from {order.status} to {new_status}")
        if (
            new_status == STATUS_DELIVERED
            and order.order_type == ORDER_TYPE_FURNITURE
            and ModuleService.is_enabled_for_tenant(tenant, "delivery_tracking")
        ):
            raise ValidationError(
                "Use the delivery board to mark furniture orders as delivered"
            )

        old = CustomOrderService.serialize(order)
        order.status = new_status
        if notes is not None:
            text = (notes or "").strip()
            order.notes = text or order.notes
        if new_status == STATUS_DELIVERED:
            order.delivered_at = utc_now_naive()

        serialized = CustomOrderService.serialize(order)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_CUSTOM_ORDER_STATUS",
            entity_type="CUSTOM_ORDER",
            entity_id=order.id,
            old_data=old,
            new_data=serialized,
        )
        db.session.commit()

        if new_status == STATUS_READY:
            NotificationService.notify_custom_order_ready(
                tenant_id=ctx.tenant_id,
                order_number=order.order_number,
                title=order.title,
                user_id=ctx.user_id,
            )
        return serialized
