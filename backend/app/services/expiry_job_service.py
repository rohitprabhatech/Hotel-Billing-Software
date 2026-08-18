"""Scheduled subscription expiry notices — CLI/cron is the source of truth.

Does not depend on a user opening the app. Idempotent per
(subscription_id, notice_type, entitlement end date).
"""

from __future__ import annotations

import logging

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.subscription import SUBSCRIPTION_EXPIRED
from app.models.subscription_notice import (
    NOTICE_EXPIRED,
    NOTICE_EXPIRING,
    SubscriptionNotice,
)
from app.repositories.subscription_notice_repository import SubscriptionNoticeRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from app.services.notification_service import (
    TYPE_SUBSCRIPTION_EXPIRED,
    TYPE_SUBSCRIPTION_EXPIRING,
    NotificationService,
)
from app.services.platform_notification_service import PlatformNotificationService
from app.services.subscription_service import SubscriptionService
from app.utils.ids import new_uuid

logger = logging.getLogger(__name__)


class ExpiryJobService:
    @staticmethod
    def run() -> dict:
        rows = SubscriptionRepository.list_all_rows()
        for row in rows:
            SubscriptionService.refresh_status(row, persist=True)
        db.session.commit()

        checked = 0
        expiring_notices = 0
        expired_notices = 0
        emails_sent = 0
        skipped = 0

        for row in rows:
            checked += 1
            serialized = SubscriptionService.serialize(row)
            if not serialized:
                skipped += 1
                continue
            end = SubscriptionService.entitlement_end(row)
            if end is None:
                skipped += 1
                continue

            period_key = end.date().isoformat()
            if serialized["status"] == SUBSCRIPTION_EXPIRED:
                sent, mail = ExpiryJobService._notify_if_needed(
                    row,
                    serialized,
                    notice_type=NOTICE_EXPIRED,
                    period_key=period_key,
                )
                expired_notices += sent
                emails_sent += mail
                if not sent:
                    skipped += 1
            elif serialized.get("is_expiring"):
                sent, mail = ExpiryJobService._notify_if_needed(
                    row,
                    serialized,
                    notice_type=NOTICE_EXPIRING,
                    period_key=period_key,
                )
                expiring_notices += sent
                emails_sent += mail
                if not sent:
                    skipped += 1
            else:
                skipped += 1

        return {
            "checked": checked,
            "expiring_notices": expiring_notices,
            "expired_notices": expired_notices,
            "emails_sent": emails_sent,
            "skipped": skipped,
        }

    @staticmethod
    def _notify_if_needed(row, serialized: dict, *, notice_type: str, period_key: str):
        if SubscriptionNoticeRepository.exists(row.id, notice_type, period_key):
            return 0, 0

        SubscriptionNoticeRepository.add(
            SubscriptionNotice(
                id=new_uuid(),
                subscription_id=row.id,
                tenant_id=row.tenant_id,
                notice_type=notice_type,
                period_key=period_key,
            )
        )
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            logger.info(
                "Duplicate expiry notice skipped subscription=%s type=%s period=%s",
                row.id,
                notice_type,
                period_key,
            )
            return 0, 0

        expired = notice_type == NOTICE_EXPIRED
        remaining = serialized.get("remaining_days")
        business = serialized.get("business_name") or "a business"
        ends_label = end_label(serialized)

        if expired:
            title = "Subscription expired"
            customer_message = (
                f"Your Business Billing subscription for {business} has expired. "
                "Sign in is still allowed. Contact Prabha Technology to renew access."
            )
            master_title = "Subscription expired"
            master_message = f"{business} subscription has expired."
            customer_type = TYPE_SUBSCRIPTION_EXPIRED
            master_type = TYPE_SUBSCRIPTION_EXPIRED
        else:
            days = remaining if remaining is not None else 0
            day_word = "day" if days == 1 else "days"
            title = "Subscription expiring soon"
            customer_message = (
                f"Your Business Billing subscription for {business} expires in "
                f"{days} {day_word}{ends_label}. Contact Prabha Technology to renew."
            )
            master_title = "Subscription expiring"
            master_message = f"{business} expires in {days} {day_word}."
            customer_type = TYPE_SUBSCRIPTION_EXPIRING
            master_type = TYPE_SUBSCRIPTION_EXPIRING

        NotificationService.create_tenant_notification(
            tenant_id=row.tenant_id,
            notification_type=customer_type,
            title=title,
            message=customer_message,
            entity_type="SUBSCRIPTION",
            entity_id=row.id,
        )
        PlatformNotificationService.create(
            notification_type=master_type,
            title=master_title,
            message=master_message,
            entity_type="TENANT",
            entity_id=row.tenant_id,
        )

        emails_sent = ExpiryJobService._email_owners(
            tenant_id=row.tenant_id,
            business_name=business,
            remaining_days=remaining,
            ends_at=ends_label.strip(" ()") if ends_label else None,
            expired=expired,
        )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            logger.info(
                "Duplicate expiry notice skipped subscription=%s type=%s period=%s",
                row.id,
                notice_type,
                period_key,
            )
            return 0, emails_sent
        return 1, emails_sent

    @staticmethod
    def _email_owners(
        *,
        tenant_id: str,
        business_name: str,
        remaining_days: int | None,
        ends_at: str | None,
        expired: bool,
    ) -> int:
        login_url = f"{current_app.config['FRONTEND_URL']}/login"
        sent = 0
        for owner in UserRepository.list_active_owners(tenant_id):
            try:
                if expired:
                    EmailService.send_subscription_expired_email(
                        to=owner.email,
                        name=owner.name,
                        business_name=business_name,
                        login_url=login_url,
                    )
                else:
                    EmailService.send_subscription_expiring_email(
                        to=owner.email,
                        name=owner.name,
                        business_name=business_name,
                        remaining_days=remaining_days or 0,
                        ends_at=ends_at,
                        login_url=login_url,
                    )
                sent += 1
            except Exception:
                logger.exception("Failed to send expiry email to %s", owner.email)
        return sent


def end_label(serialized: dict) -> str:
    raw = serialized.get("ends_at") or serialized.get("trial_ends_at")
    if not raw:
        return ""
    return f" ({raw[:10]})"
