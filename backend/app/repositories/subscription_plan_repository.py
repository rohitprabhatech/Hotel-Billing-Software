"""Subscription plan data access."""

from app.extensions import db
from app.models.subscription_plan import SubscriptionPlan


class SubscriptionPlanRepository:
    @staticmethod
    def get_by_id(plan_id: str) -> SubscriptionPlan | None:
        return db.session.get(SubscriptionPlan, plan_id)

    @staticmethod
    def list_all(*, include_inactive: bool = True) -> list[SubscriptionPlan]:
        query = db.session.query(SubscriptionPlan)
        if not include_inactive:
            query = query.filter(SubscriptionPlan.is_active.is_(True))
        return query.order_by(
            SubscriptionPlan.display_order.asc(),
            SubscriptionPlan.name.asc(),
        ).all()

    @staticmethod
    def list_public_active() -> list[SubscriptionPlan]:
        return (
            db.session.query(SubscriptionPlan)
            .filter(
                SubscriptionPlan.is_active.is_(True),
                SubscriptionPlan.is_public.is_(True),
            )
            .order_by(
                SubscriptionPlan.display_order.asc(),
                SubscriptionPlan.name.asc(),
            )
            .all()
        )

    @staticmethod
    def count_active() -> int:
        return int(
            db.session.query(SubscriptionPlan)
            .filter(SubscriptionPlan.is_active.is_(True))
            .count()
        )

    @staticmethod
    def add(row: SubscriptionPlan) -> SubscriptionPlan:
        db.session.add(row)
        return row
