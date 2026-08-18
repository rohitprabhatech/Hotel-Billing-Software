"""Master Admin in-app notifications (platform-wide, no tenant_id)."""

from app.extensions import db
from app.models.platform_notification import PlatformNotification
from app.repositories.platform_notification_repository import PlatformNotificationRepository
from app.utils.exceptions import NotFoundError
from app.utils.ids import new_uuid
from app.utils.request_context import require_master_context


class PlatformNotificationService:
    @staticmethod
    def list_notifications(*, unread_only=False, page=1, per_page=50):
        require_master_context()
        rows, total = PlatformNotificationRepository.list_all(
            unread_only=bool(unread_only),
            page=page,
            per_page=per_page,
        )
        return (
            [PlatformNotificationService.serialize(r) for r in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
                "unread_count": PlatformNotificationRepository.unread_count(),
            },
        )

    @staticmethod
    def unread_count():
        require_master_context()
        return {"unread_count": PlatformNotificationRepository.unread_count()}

    @staticmethod
    def mark_read(notification_id: str):
        require_master_context()
        row = PlatformNotificationRepository.get_by_id(notification_id)
        if row is None:
            raise NotFoundError("Notification not found")
        PlatformNotificationRepository.mark_read(row)
        db.session.commit()
        return PlatformNotificationService.serialize(row)

    @staticmethod
    def mark_all_read():
        require_master_context()
        updated = PlatformNotificationRepository.mark_all_read()
        db.session.commit()
        return {"updated": int(updated or 0)}

    @staticmethod
    def create(
        *,
        notification_type: str,
        title: str,
        message: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ):
        row = PlatformNotification(
            id=new_uuid(),
            type=notification_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            is_read=False,
        )
        PlatformNotificationRepository.add(row)
        return row

    @staticmethod
    def serialize(row: PlatformNotification):
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
