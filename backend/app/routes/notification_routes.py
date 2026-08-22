"""Notification API routes."""

from flask import Blueprint

from app.controllers import notification_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.get("")
@roles_required(ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
def list_notifications():
    return notification_controller.list_notifications()


@notifications_bp.get("/unread-count")
@roles_required(ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
def unread_count():
    return notification_controller.unread_count()


@notifications_bp.patch("/<notification_id>/read")
@roles_required(ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
def mark_read(notification_id: str):
    return notification_controller.mark_read(notification_id)


@notifications_bp.patch("/read-all")
@roles_required(ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
def mark_all_read():
    return notification_controller.mark_all_read()
