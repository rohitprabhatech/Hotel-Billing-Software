"""Idempotency log for subscription expiry notices."""

from app.extensions import db
from app.models.subscription_notice import SubscriptionNotice


class SubscriptionNoticeRepository:
    @staticmethod
    def exists(subscription_id: str, notice_type: str, period_key: str) -> bool:
        return (
            db.session.query(SubscriptionNotice.id)
            .filter(
                SubscriptionNotice.subscription_id == subscription_id,
                SubscriptionNotice.notice_type == notice_type,
                SubscriptionNotice.period_key == period_key,
            )
            .first()
            is not None
        )

    @staticmethod
    def add(row: SubscriptionNotice) -> SubscriptionNotice:
        db.session.add(row)
        return row
