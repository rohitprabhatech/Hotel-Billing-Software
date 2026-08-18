"""Platform notification data access (Master Admin)."""

from datetime import datetime, timezone

from app.extensions import db
from app.models.platform_notification import PlatformNotification


class PlatformNotificationRepository:
    @staticmethod
    def add(row: PlatformNotification) -> PlatformNotification:
        db.session.add(row)
        return row

    @staticmethod
    def get_by_id(notification_id: str) -> PlatformNotification | None:
        return db.session.get(PlatformNotification, notification_id)

    @staticmethod
    def list_all(
        *,
        unread_only: bool = False,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[PlatformNotification], int]:
        query = db.session.query(PlatformNotification)
        if unread_only:
            query = query.filter(PlatformNotification.is_read.is_(False))
        total = query.count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(PlatformNotification.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def unread_count() -> int:
        return (
            db.session.query(PlatformNotification)
            .filter(PlatformNotification.is_read.is_(False))
            .count()
        )

    @staticmethod
    def mark_read(row: PlatformNotification) -> PlatformNotification:
        if not row.is_read:
            row.is_read = True
            row.read_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return row

    @staticmethod
    def mark_all_read() -> int:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (
            db.session.query(PlatformNotification)
            .filter(PlatformNotification.is_read.is_(False))
            .update(
                {"is_read": True, "read_at": now},
                synchronize_session=False,
            )
        )
