"""Notification data access — tenant scoped."""

from datetime import datetime, timezone

from app.extensions import db
from app.models.notification import Notification


class NotificationRepository:
    @staticmethod
    def add(row: Notification) -> Notification:
        db.session.add(row)
        return row

    @staticmethod
    def get_by_id_and_tenant(notification_id: str, tenant_id: str) -> Notification | None:
        return (
            db.session.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.tenant_id == tenant_id,
            )
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        unread_only: bool = False,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Notification], int]:
        query = db.session.query(Notification).filter(Notification.tenant_id == tenant_id)
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))
        total = query.count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        rows = (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def unread_count(tenant_id: str) -> int:
        return (
            db.session.query(Notification)
            .filter(
                Notification.tenant_id == tenant_id,
                Notification.is_read.is_(False),
            )
            .count()
        )

    @staticmethod
    def has_open_stock_alert(
        tenant_id: str, *, notification_type: str, entity_id: str
    ) -> bool:
        """Duplicate control: unread alert of same type for the item still open."""
        return (
            db.session.query(Notification.id)
            .filter(
                Notification.tenant_id == tenant_id,
                Notification.type == notification_type,
                Notification.entity_type == "ITEM",
                Notification.entity_id == entity_id,
                Notification.is_read.is_(False),
            )
            .first()
            is not None
        )

    @staticmethod
    def mark_read(row: Notification) -> Notification:
        if not row.is_read:
            row.is_read = True
            row.read_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return row

    @staticmethod
    def mark_all_read(tenant_id: str) -> int:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (
            db.session.query(Notification)
            .filter(
                Notification.tenant_id == tenant_id,
                Notification.is_read.is_(False),
            )
            .update(
                {"is_read": True, "read_at": now},
                synchronize_session=False,
            )
        )

    @staticmethod
    def mark_unread_stock_alerts_read(
        tenant_id: str, *, entity_id: str, types: list[str]
    ) -> int:
        if not types:
            return 0
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (
            db.session.query(Notification)
            .filter(
                Notification.tenant_id == tenant_id,
                Notification.entity_type == "ITEM",
                Notification.entity_id == entity_id,
                Notification.type.in_(types),
                Notification.is_read.is_(False),
            )
            .update(
                {"is_read": True, "read_at": now},
                synchronize_session=False,
            )
        )
