"""Subscription data access."""

from datetime import datetime

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.subscription import (
    ACCESS_STATUSES,
    SUBSCRIPTION_EXPIRED,
    SUBSCRIPTION_TRIAL,
    Subscription,
)

_IN_CHUNK = 500


class SubscriptionRepository:
    @staticmethod
    def get_by_id(subscription_id: str) -> Subscription | None:
        return db.session.get(Subscription, subscription_id)

    @staticmethod
    def get_current_for_tenant(tenant_id: str) -> Subscription | None:
        return (
            db.session.query(Subscription)
            .filter(Subscription.tenant_id == tenant_id)
            .order_by(Subscription.created_at.desc(), Subscription.id.desc())
            .first()
        )

    @staticmethod
    def tenant_ids_with_subscription() -> set[str]:
        rows = db.session.query(Subscription.tenant_id).distinct().all()
        return {row[0] for row in rows}

    @staticmethod
    def count_active_trials(*, now: datetime) -> int:
        return int(
            db.session.query(Subscription)
            .filter(
                Subscription.status == SUBSCRIPTION_TRIAL,
                Subscription.trial_ends_at.is_not(None),
                Subscription.trial_ends_at > now,
            )
            .count()
        )

    @staticmethod
    def count_expired(*, now: datetime) -> int:
        return int(
            db.session.query(Subscription)
            .filter(Subscription.status == SUBSCRIPTION_EXPIRED)
            .count()
        )

    @staticmethod
    def count_access_ok() -> int:
        return int(
            db.session.query(Subscription)
            .filter(Subscription.status.in_(tuple(ACCESS_STATUSES)))
            .count()
        )

    @staticmethod
    def list_trials(*, now: datetime, page: int = 1, per_page: int = 25) -> tuple[list[Subscription], int]:
        query = db.session.query(Subscription).filter(
            Subscription.status == SUBSCRIPTION_TRIAL,
            Subscription.trial_ends_at.is_not(None),
            Subscription.trial_ends_at > now,
        )
        total = query.order_by(None).count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        rows = (
            query.options(joinedload(Subscription.tenant), joinedload(Subscription.plan))
            .order_by(Subscription.trial_ends_at.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def map_current_for_tenants(tenant_ids: list[str]) -> dict[str, Subscription]:
        ids = list(dict.fromkeys([tid for tid in tenant_ids if tid]))
        current: dict[str, Subscription] = {}
        if not ids:
            return current
        for offset in range(0, len(ids), _IN_CHUNK):
            chunk = ids[offset : offset + _IN_CHUNK]
            rows = (
                db.session.query(Subscription)
                .options(joinedload(Subscription.plan), joinedload(Subscription.tenant))
                .filter(Subscription.tenant_id.in_(chunk))
                .order_by(Subscription.created_at.desc(), Subscription.id.desc())
                .all()
            )
            for row in rows:
                current.setdefault(row.tenant_id, row)
        return current

    @staticmethod
    def list_all(*, page: int = 1, per_page: int = 25) -> tuple[list[Subscription], int]:
        query = db.session.query(Subscription)
        total = query.order_by(None).count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 25), 1), 100)
        rows = (
            query.order_by(Subscription.updated_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def list_all_rows() -> list[Subscription]:
        return db.session.query(Subscription).order_by(Subscription.created_at.asc()).all()

    @staticmethod
    def add(row: Subscription) -> Subscription:
        db.session.add(row)
        return row
