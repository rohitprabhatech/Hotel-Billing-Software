"""Trial / subscription entitlement helpers."""

from datetime import timedelta

from app.extensions import db
from app.models.subscription import (
    ACCESS_STATUSES,
    PAYMENT_COMPLIMENTARY,
    PAYMENT_MANUAL,
    SUBSCRIPTION_ACTIVE,
    SUBSCRIPTION_CANCELLED,
    SUBSCRIPTION_EXPIRED,
    SUBSCRIPTION_EXPIRING,
    SUBSCRIPTION_SUSPENDED,
    SUBSCRIPTION_TRIAL,
    Subscription,
)
from app.models.subscription_plan import DEFAULT_PLAN_ID
from app.repositories.subscription_plan_repository import SubscriptionPlanRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.platform_settings_service import PlatformSettingsService
from app.utils.exceptions import NotFoundError, SubscriptionInactiveError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_master_context, require_request_context
from app.utils.tokens import utc_now_naive


def _days(value, *, label: str = "Duration") -> int:
    try:
        days = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{label} must be a number") from exc
    if days < 1 or days > 365:
        raise ValidationError(f"{label} must be between 1 and 365 days")
    return days


class SubscriptionService:
    @staticmethod
    def remaining_days(ends_at, *, now=None) -> int | None:
        if ends_at is None:
            return None
        now = now or utc_now_naive()
        delta = ends_at.date() - now.date()
        return max(int(delta.days), 0)

    @staticmethod
    def entitlement_end(row: Subscription):
        if row.status == SUBSCRIPTION_TRIAL:
            return row.trial_ends_at or row.ends_at
        return row.ends_at or row.trial_ends_at

    @staticmethod
    def refresh_status(row: Subscription | None, *, now=None, persist: bool = True) -> Subscription | None:
        if row is None:
            return None
        if row.status in {SUBSCRIPTION_CANCELLED, SUBSCRIPTION_SUSPENDED}:
            return row
        now = now or utc_now_naive()
        end = SubscriptionService.entitlement_end(row)
        previous = row.status
        if end is not None and end <= now:
            row.status = SUBSCRIPTION_EXPIRED
        elif end is None:
            row.status = SUBSCRIPTION_ACTIVE
        else:
            settings = PlatformSettingsService.get_or_create()
            remaining = SubscriptionService.remaining_days(end, now=now)
            warning = int(settings.expiry_warning_days or 5)
            if remaining is not None and remaining <= warning:
                if row.status != SUBSCRIPTION_TRIAL:
                    row.status = SUBSCRIPTION_EXPIRING
            elif row.status == SUBSCRIPTION_EXPIRING:
                row.status = SUBSCRIPTION_ACTIVE
        if persist and row.status != previous:
            db.session.flush()
        return row

    @staticmethod
    def has_access(row: Subscription | None, *, now=None) -> bool:
        row = SubscriptionService.refresh_status(row, now=now, persist=True)
        return row is not None and row.status in ACCESS_STATUSES

    @staticmethod
    def enforce_access():
        ctx = require_request_context()
        row = SubscriptionRepository.get_current_for_tenant(ctx.tenant_id)
        previous = row.status if row is not None else None
        row = SubscriptionService.refresh_status(row, persist=True)
        if row is not None and row.status != previous:
            db.session.commit()
        if row is not None and row.status in ACCESS_STATUSES:
            return
        status = row.status if row else None
        raise SubscriptionInactiveError(
            "Your subscription is not active. Contact Prabha Technology to renew access.",
            details={"status": status},
        )

    @staticmethod
    def start_trial_for_new_tenant(tenant) -> Subscription | None:
        """Create a TRIAL row using *current* settings. Does not alter existing trials."""
        settings = PlatformSettingsService.get_or_create()
        if not settings.trial_enabled:
            return None
        return SubscriptionService._create_trial(tenant, days=int(settings.trial_days))

    @staticmethod
    def _create_trial(tenant, *, days: int) -> Subscription:
        now = utc_now_naive()
        ends = now + timedelta(days=days)
        row = Subscription(
            id=new_uuid(),
            tenant_id=tenant.id,
            plan_id=None,
            status=SUBSCRIPTION_TRIAL,
            starts_at=now,
            ends_at=ends,
            trial_starts_at=now,
            trial_ends_at=ends,
            price_at_purchase=None,
            payment_status=None,
            payment_provider=None,
            payment_reference=None,
        )
        SubscriptionRepository.add(row)
        db.session.flush()
        return row

    @staticmethod
    def grant_complimentary(tenant, *, plan_id: str | None = None) -> Subscription:
        now = utc_now_naive()
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        chosen_plan = plan_id or DEFAULT_PLAN_ID
        plan = SubscriptionPlanRepository.get_by_id(chosen_plan)
        plan_pk = plan.id if plan is not None else None
        if row is None:
            row = Subscription(
                id=new_uuid(),
                tenant_id=tenant.id,
                plan_id=plan_pk,
                status=SUBSCRIPTION_ACTIVE,
                starts_at=now,
                ends_at=None,
                trial_starts_at=None,
                trial_ends_at=None,
                price_at_purchase=None,
                payment_status=PAYMENT_COMPLIMENTARY,
            )
            SubscriptionRepository.add(row)
        else:
            row.plan_id = plan_pk if plan_pk is not None else row.plan_id
            row.status = SUBSCRIPTION_ACTIVE
            row.starts_at = row.starts_at or now
            row.ends_at = None
            row.payment_status = PAYMENT_COMPLIMENTARY
        db.session.flush()
        return row

    @staticmethod
    def serialize(row: Subscription | None, *, now=None) -> dict | None:
        if row is None:
            return None
        now = now or utc_now_naive()
        row = SubscriptionService.refresh_status(row, now=now, persist=False)
        ends = SubscriptionService.entitlement_end(row)
        remaining = SubscriptionService.remaining_days(ends, now=now)
        settings = PlatformSettingsService.get_or_create()
        warning = int(settings.expiry_warning_days or 5)
        is_expiring = (
            remaining is not None
            and remaining <= warning
            and row.status in {SUBSCRIPTION_TRIAL, SUBSCRIPTION_ACTIVE, SUBSCRIPTION_EXPIRING}
        )
        tenant = row.tenant
        return {
            "id": row.id,
            "tenant_id": row.tenant_id,
            "business_name": tenant.business_name if tenant else None,
            "tenant_status": tenant.status if tenant else None,
            "status": row.status,
            "plan_id": row.plan_id,
            "plan_name": row.plan.name if row.plan else None,
            "starts_at": row.starts_at.isoformat() if row.starts_at else None,
            "ends_at": row.ends_at.isoformat() if row.ends_at else None,
            "trial_starts_at": row.trial_starts_at.isoformat() if row.trial_starts_at else None,
            "trial_ends_at": row.trial_ends_at.isoformat() if row.trial_ends_at else None,
            "remaining_days": remaining,
            "is_expiring": is_expiring,
            "access_allowed": row.status in ACCESS_STATUSES,
            "is_complimentary": row.payment_status == PAYMENT_COMPLIMENTARY
            or (row.status == SUBSCRIPTION_ACTIVE and row.ends_at is None),
            "price_at_purchase": float(row.price_at_purchase)
            if row.price_at_purchase is not None
            else None,
            "payment_status": row.payment_status,
        }

    @staticmethod
    def serialize_for_tenant(tenant_id: str) -> dict | None:
        row = SubscriptionRepository.get_current_for_tenant(tenant_id)
        data = SubscriptionService.serialize(row)
        if data is None:
            return None
        data.pop("business_name", None)
        data.pop("tenant_status", None)
        return data

    @staticmethod
    def list_active_trials(*, page=1, per_page=25):
        require_master_context()
        now = utc_now_naive()
        rows, total = SubscriptionRepository.list_trials(now=now, page=page, per_page=per_page)
        return (
            [SubscriptionService.serialize(r, now=now) for r in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 25), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def list_businesses(*, status: str | None = None, q: str | None = None, page=1, per_page=25):
        require_master_context()
        now = utc_now_naive()
        tenants, total = TenantRepository.list_all(q=q, page=1, per_page=500)
        rows = []
        wanted = (status or "").strip().upper() or None
        for tenant in tenants:
            sub = SubscriptionRepository.get_current_for_tenant(tenant.id)
            SubscriptionService.refresh_status(sub, now=now, persist=True)
            payload = {
                "id": tenant.id,
                "business_name": tenant.business_name,
                "name": tenant.name,
                "email": tenant.email,
                "tenant_status": tenant.status,
                "subscription": SubscriptionService.serialize(sub, now=now),
            }
            effective = payload["subscription"]["status"] if payload["subscription"] else "NONE"
            if wanted == "EXPIRING":
                if not payload["subscription"] or not payload["subscription"]["is_expiring"]:
                    continue
            elif wanted == "NONE":
                if payload["subscription"] is not None:
                    continue
            elif wanted and effective != wanted:
                continue
            rows.append(payload)
        total = len(rows)
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 25), 1), 100)
        start = (page - 1) * per_page
        return rows[start : start + per_page], {
            "page": page,
            "per_page": per_page,
            "total": total,
        }

    @staticmethod
    def list_expiring(*, page=1, per_page=25):
        return SubscriptionService.list_businesses(status="EXPIRING", page=page, per_page=per_page)

    @staticmethod
    def get_business(tenant_id: str):
        require_master_context()
        tenant = TenantRepository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundError("Business not found")
        sub = SubscriptionRepository.get_current_for_tenant(tenant.id)
        SubscriptionService.refresh_status(sub, persist=True)
        db.session.commit()
        return {
            "id": tenant.id,
            "business_name": tenant.business_name,
            "name": tenant.name,
            "email": tenant.email,
            "tenant_status": tenant.status,
            "subscription": SubscriptionService.serialize(sub),
        }

    @staticmethod
    def _require_tenant(tenant_id: str):
        tenant = TenantRepository.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundError("Business not found")
        return tenant

    @staticmethod
    def _require_active_plan(plan_id: str):
        plan = SubscriptionPlanRepository.get_by_id(plan_id)
        if plan is None:
            raise NotFoundError("Plan not found")
        if not plan.is_active:
            raise ValidationError("Inactive plans cannot be assigned to new subscriptions")
        return plan

    @staticmethod
    def assign_plan(tenant_id: str, *, plan_id: str, days: int | None = None):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        plan = SubscriptionService._require_active_plan(plan_id)
        now = utc_now_naive()
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        ends = None
        if days is not None:
            ends = now + timedelta(days=_days(days, label="Paid duration"))
        if row is None:
            row = Subscription(
                id=new_uuid(),
                tenant_id=tenant.id,
                plan_id=plan.id,
                status=SUBSCRIPTION_ACTIVE,
                starts_at=now,
                ends_at=ends,
                price_at_purchase=plan.price if ends is not None else None,
                payment_status=PAYMENT_COMPLIMENTARY if ends is None else PAYMENT_MANUAL,
            )
            SubscriptionRepository.add(row)
        else:
            row.plan_id = plan.id
            if ends is not None:
                row.ends_at = ends
                row.starts_at = now
                row.status = SUBSCRIPTION_ACTIVE
                row.price_at_purchase = plan.price
                row.payment_status = PAYMENT_MANUAL
            else:
                row.status = SUBSCRIPTION_ACTIVE
                row.ends_at = None
                row.payment_status = PAYMENT_COMPLIMENTARY
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def start_or_extend_trial(tenant_id: str, *, days: int):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        duration = _days(days, label="Trial duration")
        now = utc_now_naive()
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        extra = timedelta(days=duration)
        if row is None:
            row = SubscriptionService._create_trial(tenant, days=duration)
        elif (
            row.status == SUBSCRIPTION_TRIAL
            and (row.trial_ends_at or row.ends_at)
            and ((row.trial_ends_at or row.ends_at) > now)
        ):
            base = row.trial_ends_at or row.ends_at
            row.trial_ends_at = base + extra
            row.ends_at = row.trial_ends_at
            row.status = SUBSCRIPTION_TRIAL
        else:
            row.status = SUBSCRIPTION_TRIAL
            row.trial_starts_at = now
            row.trial_ends_at = now + extra
            row.starts_at = now
            row.ends_at = row.trial_ends_at
            row.payment_status = None
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def renew(tenant_id: str, *, days: int, plan_id: str | None = None):
        """Manual paid period. No payment gateway — Master records the renewal."""
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        duration = _days(days, label="Renewal duration")
        now = utc_now_naive()
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        if plan_id:
            plan = SubscriptionService._require_active_plan(plan_id)
        elif row and row.plan_id:
            plan = SubscriptionPlanRepository.get_by_id(row.plan_id)
            if plan is None:
                raise ValidationError("Assign an active plan before renewing")
        else:
            raise ValidationError("A plan is required to renew")
        extra = timedelta(days=duration)
        if row is None:
            row = Subscription(
                id=new_uuid(),
                tenant_id=tenant.id,
                plan_id=plan.id,
                status=SUBSCRIPTION_ACTIVE,
                starts_at=now,
                ends_at=now + extra,
                price_at_purchase=plan.price,
                payment_status=PAYMENT_MANUAL,
            )
            SubscriptionRepository.add(row)
        else:
            base = now
            current_end = row.ends_at
            if current_end is not None and current_end > now and row.status in ACCESS_STATUSES:
                base = current_end
            row.plan_id = plan.id
            row.status = SUBSCRIPTION_ACTIVE
            row.starts_at = now
            row.ends_at = base + extra
            row.price_at_purchase = plan.price
            row.payment_status = PAYMENT_MANUAL
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def cancel(tenant_id: str):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        if row is None:
            raise NotFoundError("Subscription not found")
        row.status = SUBSCRIPTION_CANCELLED
        row.ends_at = utc_now_naive()
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def count_expiring(*, now=None) -> int:
        now = now or utc_now_naive()
        count = 0
        rows = db.session.query(Subscription).all()
        for row in rows:
            data = SubscriptionService.serialize(row, now=now)
            if data and data["is_expiring"]:
                count += 1
        return count

    @staticmethod
    def count_expired(*, now=None) -> int:
        now = now or utc_now_naive()
        count = 0
        rows = db.session.query(Subscription).all()
        for row in rows:
            SubscriptionService.refresh_status(row, now=now, persist=True)
            if row.status == SUBSCRIPTION_EXPIRED:
                count += 1
        return count
