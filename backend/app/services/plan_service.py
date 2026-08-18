"""Master Admin subscription plan catalog."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app.extensions import db
from app.models.subscription import Subscription
from app.models.subscription_plan import (
    BILLING_CYCLES,
    BILLING_CYCLE_MONTHLY,
    SubscriptionPlan,
)
from app.repositories.subscription_plan_repository import SubscriptionPlanRepository
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_master_context


def _money(value) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError("A valid plan price is required") from exc
    if amount < 0:
        raise ValidationError("Plan price cannot be negative")
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _features(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [part.strip() for part in value.replace("\r", "").split("\n")]
    elif isinstance(value, list):
        items = [str(part).strip() for part in value]
    else:
        raise ValidationError("Features must be a list of strings")
    return [item for item in items if item][:40]


class PlanService:
    @staticmethod
    def list_plans(*, include_inactive: bool = True):
        require_master_context()
        rows = SubscriptionPlanRepository.list_all(include_inactive=include_inactive)
        return [PlanService.serialize(row) for row in rows]

    @staticmethod
    def list_public_plans():
        rows = SubscriptionPlanRepository.list_public_active()
        return [PlanService.serialize_public(row) for row in rows]

    @staticmethod
    def get_plan(plan_id: str):
        require_master_context()
        row = SubscriptionPlanRepository.get_by_id(plan_id)
        if row is None:
            raise NotFoundError("Plan not found")
        return PlanService.serialize(row, detail=True)

    @staticmethod
    def create(payload: dict):
        require_master_context()
        row = SubscriptionPlan(
            id=new_uuid(),
            **PlanService._attrs_from_payload(payload, partial=False),
        )
        SubscriptionPlanRepository.add(row)
        db.session.commit()
        return PlanService.serialize(row, detail=True)

    @staticmethod
    def update(plan_id: str, payload: dict):
        require_master_context()
        row = SubscriptionPlanRepository.get_by_id(plan_id)
        if row is None:
            raise NotFoundError("Plan not found")
        for key, value in PlanService._attrs_from_payload(payload, partial=True).items():
            setattr(row, key, value)
        db.session.commit()
        return PlanService.serialize(row, detail=True)

    @staticmethod
    def set_active(plan_id: str, is_active: bool):
        require_master_context()
        row = SubscriptionPlanRepository.get_by_id(plan_id)
        if row is None:
            raise NotFoundError("Plan not found")
        row.is_active = bool(is_active)
        db.session.commit()
        return PlanService.serialize(row, detail=True)

    @staticmethod
    def _attrs_from_payload(payload: dict, *, partial: bool) -> dict:
        data = {}
        if not partial or "name" in payload:
            name = (payload.get("name") or "").strip()
            if not name:
                raise ValidationError("Plan name is required")
            if len(name) > 120:
                raise ValidationError("Plan name is too long")
            data["name"] = name
        if not partial or "description" in payload:
            description = (payload.get("description") or "").strip()
            data["description"] = description or None
        if not partial or "price" in payload:
            if payload.get("price") is None and not partial:
                raise ValidationError("Plan price is required")
            if payload.get("price") is not None:
                data["price"] = _money(payload.get("price"))
        if not partial or "billing_cycle" in payload:
            cycle = (payload.get("billing_cycle") or BILLING_CYCLE_MONTHLY).strip().upper()
            if cycle not in BILLING_CYCLES:
                raise ValidationError("Billing cycle must be MONTHLY or YEARLY")
            data["billing_cycle"] = cycle
        if not partial or "trial_eligible" in payload:
            data["trial_eligible"] = bool(payload.get("trial_eligible", True))
        if not partial or "is_public" in payload:
            data["is_public"] = bool(payload.get("is_public", True))
        if not partial or "is_active" in payload:
            data["is_active"] = bool(payload.get("is_active", True))
        if not partial or "display_order" in payload:
            try:
                order = int(payload.get("display_order", 0) or 0)
            except (TypeError, ValueError) as exc:
                raise ValidationError("Display order must be a number") from exc
            if order < 0 or order > 9999:
                raise ValidationError("Display order must be between 0 and 9999")
            data["display_order"] = order
        if not partial or "features" in payload:
            data["features"] = _features(payload.get("features"))
        data.setdefault("currency", "INR")
        return data

    @staticmethod
    def serialize(row: SubscriptionPlan, *, detail: bool = False) -> dict:
        subscriber_count = int(
            db.session.query(Subscription).filter(Subscription.plan_id == row.id).count()
        )
        data = {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "price": float(row.price),
            "currency": row.currency or "INR",
            "billing_cycle": row.billing_cycle,
            "trial_eligible": bool(row.trial_eligible),
            "is_public": bool(row.is_public),
            "is_active": bool(row.is_active),
            "display_order": int(row.display_order or 0),
            "features": list(row.features or []),
            "subscriber_count": subscriber_count,
        }
        if detail:
            data["updated_at"] = row.updated_at.isoformat() if row.updated_at else None
        return data

    @staticmethod
    def serialize_public(row: SubscriptionPlan) -> dict:
        return {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "price": float(row.price),
            "currency": row.currency or "INR",
            "billing_cycle": row.billing_cycle,
            "trial_eligible": bool(row.trial_eligible),
            "display_order": int(row.display_order or 0),
            "features": list(row.features or []),
        }
