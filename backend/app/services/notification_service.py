"""In-app notifications for stock and operational events."""

from decimal import Decimal

from app.extensions import db
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.utils.exceptions import NotFoundError
from app.utils.ids import new_uuid
from app.utils.request_context import require_request_context

TYPE_LOW_STOCK = "LOW_STOCK"
TYPE_OUT_OF_STOCK = "OUT_OF_STOCK"
TYPE_INSUFFICIENT_STOCK_ATTEMPT = "INSUFFICIENT_STOCK_ATTEMPT"
TYPE_WHATSAPP_DELIVERY_FAILED = "WHATSAPP_DELIVERY_FAILED"
TYPE_EMAIL_DELIVERY_FAILED = "EMAIL_DELIVERY_FAILED"
TYPE_SUBSCRIPTION_EXPIRING = "SUBSCRIPTION_EXPIRING"
TYPE_SUBSCRIPTION_EXPIRED = "SUBSCRIPTION_EXPIRED"


class NotificationService:
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
