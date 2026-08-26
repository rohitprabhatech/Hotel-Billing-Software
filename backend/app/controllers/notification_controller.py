"""Notification HTTP controllers."""

from flask import request

from app.services.notification_service import NotificationService
from app.utils.responses import success_response


def list_templates():
    industry_only = str(request.args.get("industry_only", "")).lower() in {
        "1",
        "true",
        "yes",
    }
    return success_response(
        data=NotificationService.list_templates(industry_only=industry_only)
    )


def list_notifications():
    unread_only = str(request.args.get("unread_only", "")).lower() in {"1", "true", "yes"}
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    data, meta = NotificationService.list_notifications(
        unread_only=unread_only,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def unread_count():
    return success_response(data=NotificationService.unread_count())


def mark_read(notification_id: str):
    return success_response(data=NotificationService.mark_read(notification_id))


def mark_all_read():
    return success_response(data=NotificationService.mark_all_read())
