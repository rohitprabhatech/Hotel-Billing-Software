"""In-app notifications for stock and operational events."""

from decimal import Decimal

from app.constants.notification_templates import (
    NOTIFICATION_TEMPLATES,
    list_templates as catalog_list_templates,
)
from app.extensions import db
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.module_service import ModuleService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_request_context

TYPE_LOW_STOCK = "LOW_STOCK"
TYPE_OUT_OF_STOCK = "OUT_OF_STOCK"
TYPE_INSUFFICIENT_STOCK_ATTEMPT = "INSUFFICIENT_STOCK_ATTEMPT"
TYPE_WHATSAPP_DELIVERY_FAILED = "WHATSAPP_DELIVERY_FAILED"
TYPE_EMAIL_DELIVERY_FAILED = "EMAIL_DELIVERY_FAILED"
TYPE_SUBSCRIPTION_EXPIRING = "SUBSCRIPTION_EXPIRING"
TYPE_SUBSCRIPTION_EXPIRED = "SUBSCRIPTION_EXPIRED"
TYPE_BATCH_EXPIRING = "BATCH_EXPIRING"
TYPE_BATCH_EXPIRED = "BATCH_EXPIRED"
TYPE_CREDIT_DUE = "CREDIT_DUE"
TYPE_REPAIR_READY = "REPAIR_READY"
TYPE_INSTALLATION_SCHEDULED = "INSTALLATION_SCHEDULED"
TYPE_INSTALLATION_COMPLETED = "INSTALLATION_COMPLETED"
TYPE_CUSTOM_ORDER_DELIVERY = "CUSTOM_ORDER_DELIVERY"
TYPE_CUSTOM_ORDER_READY = "CUSTOM_ORDER_READY"
TYPE_DELIVERY_OUT_FOR_DELIVERY = "DELIVERY_OUT_FOR_DELIVERY"
TYPE_DELIVERY_COMPLETED = "DELIVERY_COMPLETED"
TYPE_TRAVEL_BOOKING_CONFIRMED = "TRAVEL_BOOKING_CONFIRMED"
TYPE_TRAVEL_PAYMENT_DUE = "TRAVEL_PAYMENT_DUE"
TYPE_KOT_READY = "KOT_READY"


class NotificationService:
    @staticmethod
    def list_templates(*, industry_only: bool = False):
        """Module-filtered template catalog for the current tenant (BIZ-63)."""
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        enabled = set(ModuleService.enabled_codes_for_tenant(tenant))
        rows = []
        for row in catalog_list_templates(industry_only=industry_only):
            module = row["module"]
            # core_* always available; industry modules must be enabled
            if module.startswith("core_") or module in enabled:
                rows.append({**row, "enabled": True})
        return {
            "templates": rows,
            "enabled_modules": sorted(enabled),
            "industry_count": sum(1 for row in rows if row["industry"]),
        }

    @staticmethod
    def emit_template(
        *,
        key: str,
        tenant_id: str,
        entity_id: str,
        context: dict,
        user_id: str | None = None,
        entity_type_override: str | None = None,
    ):
        """
        Emit a registered template with dedupe / cooldown rate limits.
        Returns the Notification row, or None when suppressed.
        """
        tpl = NOTIFICATION_TEMPLATES.get(key)
        if tpl is None:
            raise ValidationError(f"Unknown notification template: {key}")
        entity_type = entity_type_override or tpl.get("entity_type")
        notification_type = tpl["type"]
        if not entity_id or not entity_type:
            raise ValidationError("entity_id and entity_type are required for template emit")

        if tpl.get("dedupe_open") and NotificationRepository.has_open_alert(
            tenant_id,
            notification_type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
        ):
            return None
        cooldown = int(tpl.get("cooldown_seconds") or 0)
        if cooldown and NotificationRepository.has_recent_alert(
            tenant_id,
            notification_type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
            within_seconds=cooldown,
        ):
            return None

        try:
            title = tpl["title"].format(**context)
            message = tpl["message"].format(**context)
        except KeyError as exc:
            raise ValidationError(
                f"Missing template context for '{key}': {exc.args[0]}"
            ) from exc

        return NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=notification_type,
            title=title[:160],
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
        )

    @staticmethod
    def list_notifications(*, unread_only=False, page=1, per_page=50):
        ctx = require_request_context()
        rows, total = NotificationRepository.list_by_tenant(
            ctx.tenant_id,
            unread_only=bool(unread_only),
            page=page,
            per_page=per_page,
        )
        return (
            [NotificationService.serialize(r) for r in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
                "unread_count": NotificationRepository.unread_count(ctx.tenant_id),
            },
        )

    @staticmethod
    def unread_count():
        ctx = require_request_context()
        return {"unread_count": NotificationRepository.unread_count(ctx.tenant_id)}

    @staticmethod
    def mark_read(notification_id: str):
        ctx = require_request_context()
        row = NotificationRepository.get_by_id_and_tenant(notification_id, ctx.tenant_id)
        if row is None:
            raise NotFoundError("Notification not found")
        NotificationRepository.mark_read(row)
        db.session.commit()
        return NotificationService.serialize(row)

    @staticmethod
    def mark_all_read():
        ctx = require_request_context()
        updated = NotificationRepository.mark_all_read(ctx.tenant_id)
        db.session.commit()
        return {"updated": int(updated or 0)}

    @staticmethod
    def create_tenant_notification(
        *,
        tenant_id: str,
        notification_type: str,
        title: str,
        message: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        user_id: str | None = None,
    ):
        row = Notification(
            id=new_uuid(),
            tenant_id=tenant_id,
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            is_read=False,
        )
        NotificationRepository.add(row)
        return row

    @staticmethod
    def resolve_stock_alerts_if_recovered(*, tenant_id: str, item, new_stock: Decimal | None):
        """Mark open LOW/OUT alerts read when stock recovers above thresholds."""
        if new_stock is None:
            return
        new_stock = Decimal(new_stock)
        if new_stock > 0:
            NotificationRepository.mark_unread_stock_alerts_read(
                tenant_id,
                entity_id=item.id,
                types=[TYPE_OUT_OF_STOCK],
            )
        minimum = item.minimum_stock_level
        if minimum is None or new_stock > Decimal(minimum):
            NotificationRepository.mark_unread_stock_alerts_read(
                tenant_id,
                entity_id=item.id,
                types=[TYPE_LOW_STOCK],
            )

    @staticmethod
    def notify_stock_transition(
        *,
        tenant_id: str,
        item,
        previous: Decimal | None,
        new_stock: Decimal | None,
    ):
        """
        Create LOW_STOCK / OUT_OF_STOCK on meaningful crossings only.
        Rule: low when stock_quantity <= minimum_stock_level (when both set).
        Also clears open alerts when stock recovers.
        """
        if previous is None or new_stock is None:
            return

        NotificationService.resolve_stock_alerts_if_recovered(
            tenant_id=tenant_id, item=item, new_stock=new_stock
        )

        name = item.name
        # Out of stock: crossed into zero
        if previous > 0 and new_stock <= 0:
            if not NotificationRepository.has_open_stock_alert(
                tenant_id, notification_type=TYPE_OUT_OF_STOCK, entity_id=item.id
            ):
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_OUT_OF_STOCK,
                    title="Out of stock",
                    message=f"Out of stock: {name} is currently unavailable.",
                    entity_type="ITEM",
                    entity_id=item.id,
                )
            return

        minimum = item.minimum_stock_level
        if minimum is None:
            return
        minimum = Decimal(minimum)
        # Low stock: crossed from above minimum into <= minimum (and still > 0)
        if previous > minimum and new_stock <= minimum and new_stock > 0:
            if not NotificationRepository.has_open_stock_alert(
                tenant_id, notification_type=TYPE_LOW_STOCK, entity_id=item.id
            ):
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_LOW_STOCK,
                    title="Low stock",
                    message=(
                        f"Low stock: {name} has only {float(new_stock):g} units remaining "
                        f"(minimum {float(minimum):g})."
                    ),
                    entity_type="ITEM",
                    entity_id=item.id,
                )

    @staticmethod
    def notify_variant_stock(
        *,
        tenant_id: str,
        item,
        variant,
        previous: Decimal | None,
        new_stock: Decimal | None,
    ):
        """LOW_STOCK / OUT_OF_STOCK for a size/color row (BIZ-25)."""
        if previous is None or new_stock is None:
            return
        label = f"{item.name} ({variant.size}/{variant.color})"
        entity_id = variant.id
        NotificationService.resolve_stock_alerts_if_recovered(
            tenant_id=tenant_id, item=item, new_stock=Decimal(item.stock_quantity or 0)
        )
        if previous > 0 and new_stock <= 0:
            if not NotificationRepository.has_open_stock_alert(
                tenant_id, notification_type=TYPE_OUT_OF_STOCK, entity_id=entity_id
            ):
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_OUT_OF_STOCK,
                    title="Out of stock",
                    message=f"Out of stock: {label} is currently unavailable.",
                    entity_type="ITEM_VARIANT",
                    entity_id=entity_id,
                )
            return
        minimum = item.minimum_stock_level
        if minimum is None:
            return
        minimum = Decimal(minimum)
        if previous > minimum and new_stock <= minimum and new_stock > 0:
            if not NotificationRepository.has_open_stock_alert(
                tenant_id, notification_type=TYPE_LOW_STOCK, entity_id=entity_id
            ):
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_LOW_STOCK,
                    title="Low stock",
                    message=(
                        f"Low stock: {label} has only {float(new_stock):g} units remaining "
                        f"(minimum {float(minimum):g})."
                    ),
                    entity_type="ITEM_VARIANT",
                    entity_id=entity_id,
                )

    @staticmethod
    def notify_warehouse_stock_transition(
        *,
        tenant_id: str,
        item,
        warehouse,
        stock_id: str,
        previous: Decimal | None,
        new_stock: Decimal | None,
    ):
        """LOW_STOCK / OUT_OF_STOCK for a warehouse balance (BIZ-53)."""
        if previous is None or new_stock is None or not stock_id:
            return
        previous = Decimal(previous)
        new_stock = Decimal(new_stock)
        wh_label = warehouse.code if warehouse else "warehouse"
        label = f"{item.name} @ {wh_label}"
        entity_type = "WAREHOUSE_STOCK"

        if new_stock > 0:
            NotificationRepository.mark_unread_stock_alerts_read(
                tenant_id,
                entity_id=stock_id,
                types=[TYPE_OUT_OF_STOCK],
                entity_type=entity_type,
            )
        minimum = item.minimum_stock_level
        if minimum is None or new_stock > Decimal(minimum):
            NotificationRepository.mark_unread_stock_alerts_read(
                tenant_id,
                entity_id=stock_id,
                types=[TYPE_LOW_STOCK],
                entity_type=entity_type,
            )

        if previous > 0 and new_stock <= 0:
            if not NotificationRepository.has_open_alert(
                tenant_id,
                notification_type=TYPE_OUT_OF_STOCK,
                entity_type=entity_type,
                entity_id=stock_id,
            ):
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_OUT_OF_STOCK,
                    title="Out of stock (warehouse)",
                    message=f"Out of stock: {label} is currently unavailable at this location.",
                    entity_type=entity_type,
                    entity_id=stock_id,
                )
            return
        if minimum is None:
            return
        minimum = Decimal(minimum)
        if previous > minimum and new_stock <= minimum and new_stock > 0:
            if not NotificationRepository.has_open_alert(
                tenant_id,
                notification_type=TYPE_LOW_STOCK,
                entity_type=entity_type,
                entity_id=stock_id,
            ):
                NotificationService.create_tenant_notification(
                    tenant_id=tenant_id,
                    notification_type=TYPE_LOW_STOCK,
                    title="Low stock (warehouse)",
                    message=(
                        f"Low stock: {label} has only {float(new_stock):g} units remaining "
                        f"(minimum {float(minimum):g})."
                    ),
                    entity_type=entity_type,
                    entity_id=stock_id,
                )

    @staticmethod
    def notify_insufficient_attempt(
        *,
        tenant_id: str,
        item_name: str,
        item_id: str | None,
        available,
        requested,
        user_id: str | None = None,
    ):
        NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=TYPE_INSUFFICIENT_STOCK_ATTEMPT,
            title="Insufficient stock attempt",
            message=(
                f"Bill blocked for {item_name}: available {float(available):g}, "
                f"requested {float(requested):g}."
            ),
            entity_type="ITEM" if item_id else None,
            entity_id=item_id,
            user_id=user_id,
        )

    @staticmethod
    def notify_whatsapp_delivery_failed(
        *,
        tenant_id: str,
        bill_id: str,
        delivery_id: str,
        bill_number: str | None = None,
        error_message: str | None = None,
        recipient_masked: str | None = None,
    ):
        """One unread alert per failed delivery attempt (entity = delivery id)."""
        if NotificationRepository.has_open_alert(
            tenant_id,
            notification_type=TYPE_WHATSAPP_DELIVERY_FAILED,
            entity_type="BILL_DELIVERY",
            entity_id=delivery_id,
        ):
            return None
        label = bill_number or bill_id
        reason = (error_message or "WhatsApp delivery failed").strip()[:200]
        phone = f" to {recipient_masked}" if recipient_masked else ""
        return NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=TYPE_WHATSAPP_DELIVERY_FAILED,
            title="WhatsApp delivery failed",
            message=f"Bill #{label}{phone}: {reason}",
            entity_type="BILL_DELIVERY",
            entity_id=delivery_id,
        )

    @staticmethod
    def notify_email_delivery_failed(
        *,
        tenant_id: str,
        bill_id: str,
        delivery_id: str,
        bill_number: str | None = None,
        error_message: str | None = None,
        recipient_masked: str | None = None,
    ):
        """One unread alert per failed email delivery attempt (entity = delivery id)."""
        if NotificationRepository.has_open_alert(
            tenant_id,
            notification_type=TYPE_EMAIL_DELIVERY_FAILED,
            entity_type="BILL_DELIVERY",
            entity_id=delivery_id,
        ):
            return None
        label = bill_number or bill_id
        reason = (error_message or "Email delivery failed").strip()[:200]
        to = f" to {recipient_masked}" if recipient_masked else ""
        return NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=TYPE_EMAIL_DELIVERY_FAILED,
            title="Email delivery failed",
            message=f"Bill #{label}{to}: {reason}",
            entity_type="BILL_DELIVERY",
            entity_id=delivery_id,
        )

    @staticmethod
    def notify_credit_due(
        *,
        tenant_id: str,
        customer_id: str,
        customer_name: str,
        amount,
        balance_after,
        bill_number: str | None = None,
    ):
        label = bill_number or ""
        bill_part = f" Bill #{label}." if label else ""
        NotificationService.emit_template(
            key="credit_due",
            tenant_id=tenant_id,
            entity_id=customer_id,
            context={
                "customer_name": customer_name,
                "amount": float(amount),
                "bill_part": bill_part,
                "balance_after": float(balance_after),
            },
        )

    @staticmethod
    def notify_repair_ready(
        *,
        tenant_id: str,
        repair_number: str,
        serial: str,
        user_id: str | None = None,
    ):
        serial_label = serial or "unit"
        NotificationService.emit_template(
            key="repair_ready",
            tenant_id=tenant_id,
            entity_id=repair_number,
            context={"repair_number": repair_number, "serial": serial_label},
            user_id=user_id,
        )

    @staticmethod
    def notify_kot_ready(
        *,
        tenant_id: str,
        kot_id: str,
        kot_number: str,
        order_number: str,
        table_code: str | None = None,
        user_id: str | None = None,
    ):
        table_part = f" (table {table_code})" if table_code else ""
        NotificationService.emit_template(
            key="kot_ready",
            tenant_id=tenant_id,
            entity_id=kot_id,
            context={
                "kot_number": kot_number,
                "order_number": order_number or "—",
                "table_part": table_part,
            },
            user_id=user_id,
        )

    @staticmethod
    def notify_installation_scheduled(
        *,
        tenant_id: str,
        installation_number: str,
        serial: str,
        scheduled_at: str,
        user_id: str | None = None,
    ):
        serial_label = serial or "unit"
        NotificationService.emit_template(
            key="installation_scheduled",
            tenant_id=tenant_id,
            entity_id=installation_number,
            context={
                "installation_number": installation_number,
                "serial": serial_label,
                "scheduled_at": scheduled_at,
            },
            user_id=user_id,
        )

    @staticmethod
    def notify_installation_completed(
        *,
        tenant_id: str,
        installation_number: str,
        serial: str,
        user_id: str | None = None,
    ):
        serial_label = serial or "unit"
        NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=TYPE_INSTALLATION_COMPLETED,
            title="Installation completed",
            message=f"{installation_number}: {serial_label} installation is done.",
            entity_type="INSTALLATION_ORDER",
            entity_id=installation_number,
            user_id=user_id,
        )

    @staticmethod
    def notify_custom_order_delivery(
        *,
        tenant_id: str,
        order_number: str,
        title: str,
        delivery_at: str,
        user_id: str | None = None,
    ):
        NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=TYPE_CUSTOM_ORDER_DELIVERY,
            title="Custom order delivery scheduled",
            message=f"{order_number}: {title} due {delivery_at}.",
            entity_type="CUSTOM_ORDER",
            entity_id=order_number,
            user_id=user_id,
        )

    @staticmethod
    def notify_custom_order_ready(
        *,
        tenant_id: str,
        order_number: str,
        title: str,
        user_id: str | None = None,
    ):
        NotificationService.emit_template(
            key="custom_order_ready",
            tenant_id=tenant_id,
            entity_id=order_number,
            context={"order_number": order_number, "title": title},
            user_id=user_id,
        )

    @staticmethod
    def notify_delivery_out_for_delivery(
        *,
        tenant_id: str,
        delivery_number: str,
        customer_name: str,
        user_id: str | None = None,
    ):
        NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=TYPE_DELIVERY_OUT_FOR_DELIVERY,
            title="Out for delivery",
            message=f"{delivery_number}: {customer_name} — order is on the way.",
            entity_type="DELIVERY_JOB",
            entity_id=delivery_number,
            user_id=user_id,
        )

    @staticmethod
    def notify_delivery_completed(
        *,
        tenant_id: str,
        delivery_number: str,
        customer_name: str,
        user_id: str | None = None,
    ):
        NotificationService.create_tenant_notification(
            tenant_id=tenant_id,
            notification_type=TYPE_DELIVERY_COMPLETED,
            title="Delivery completed",
            message=f"{delivery_number}: {customer_name} — furniture delivered.",
            entity_type="DELIVERY_JOB",
            entity_id=delivery_number,
            user_id=user_id,
        )

    @staticmethod
    def notify_travel_booking_confirmed(
        *,
        tenant_id: str,
        booking_number: str,
        package_name: str,
        customer_name: str,
        user_id: str | None = None,
    ):
        NotificationService.emit_template(
            key="travel_booking_confirmed",
            tenant_id=tenant_id,
            entity_id=booking_number,
            context={
                "booking_number": booking_number,
                "package_name": package_name,
                "customer_name": customer_name,
            },
            user_id=user_id,
        )

    @staticmethod
    def notify_travel_payment_due(
        *,
        tenant_id: str,
        booking_number: str,
        customer_name: str,
        remaining,
        user_id: str | None = None,
    ):
        NotificationService.emit_template(
            key="travel_payment_due",
            tenant_id=tenant_id,
            entity_id=booking_number,
            context={
                "booking_number": booking_number,
                "customer_name": customer_name,
                "remaining": float(remaining),
            },
            user_id=user_id,
        )

    @staticmethod
    def serialize(row: Notification):
        return {
            "id": row.id,
            "type": row.type,
            "title": row.title,
            "message": row.message,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "is_read": row.is_read,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "read_at": row.read_at.isoformat() if row.read_at else None,
        }
