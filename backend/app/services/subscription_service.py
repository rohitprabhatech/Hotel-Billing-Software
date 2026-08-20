"""Trial / subscription entitlement helpers."""

from datetime import timedelta

from app.extensions import db
from app.models.platform_audit_log import ACTION_SUBSCRIPTION_UPDATED
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
from app.services.platform_audit_service import PlatformAuditService
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


def _subscription_snapshot(row: Subscription | None) -> dict | None:
    if row is None:
        return None
    return {
        "id": row.id,
        "status": row.status,
        "plan_id": row.plan_id,
        "ends_at": row.ends_at.isoformat() if row.ends_at else None,
        "trial_ends_at": row.trial_ends_at.isoformat() if row.trial_ends_at else None,
        "payment_status": row.payment_status,
        "price_at_purchase": float(row.price_at_purchase) if row.price_at_purchase is not None else None,
    }


class SubscriptionService:
    TENANT_LIST_STATUSES = {"ACTIVE", "SUSPENDED"}

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
    def list_businesses(
        *,
        status: str | None = None,
        tenant_status: str | None = None,
        q: str | None = None,
        page=1,
        per_page=25,
    ):
        require_master_context()
        now = utc_now_naive()
        wanted = (status or "").strip().upper() or None
        account = (tenant_status or "").strip().upper() or None
        if account and account not in SubscriptionService.TENANT_LIST_STATUSES:
            raise ValidationError("tenant_status must be ACTIVE or SUSPENDED")
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 25), 1), 100)

        if not wanted:
            tenants, total = TenantRepository.list_all(
                q=q, tenant_status=account, page=page, per_page=per_page
            )
            rows = SubscriptionService._business_payloads(tenants, now=now)
            return rows, {"page": page, "per_page": per_page, "total": total}

        tenant_ids = TenantRepository.list_ids_matching(q=q, tenant_status=account)
        subs = SubscriptionRepository.map_current_for_tenants(tenant_ids)
        matched: list[str] = []
        dirty = False
        for tenant_id in tenant_ids:
            sub = subs.get(tenant_id)
            previous = sub.status if sub is not None else None
            SubscriptionService.refresh_status(sub, now=now, persist=True)
            if sub is not None and sub.status != previous:
                dirty = True
            if SubscriptionService._status_matches(sub, wanted, now=now):
                matched.append(tenant_id)
        if dirty:
            db.session.commit()
        total = len(matched)
        start = (page - 1) * per_page
        page_ids = matched[start : start + per_page]
        tenants = TenantRepository.get_many_ordered(page_ids)
        rows = SubscriptionService._business_payloads(
            tenants, now=now, subs=subs, persist=False
        )
        return rows, {"page": page, "per_page": per_page, "total": total}

    @staticmethod
    def _status_matches(sub, wanted: str, *, now) -> bool:
        if wanted == "NONE":
            return sub is None
        if sub is None:
            return False
        data = SubscriptionService.serialize(sub, now=now)
        if wanted == "EXPIRING":
            return bool(data and data["is_expiring"])
        return data["status"] == wanted

    @staticmethod
    def _business_payloads(tenants, *, now, subs=None, persist: bool = True) -> list[dict]:
        if subs is None:
            subs = SubscriptionRepository.map_current_for_tenants(
                [tenant.id for tenant in tenants]
            )
        rows = []
        dirty = False
        for tenant in tenants:
            sub = subs.get(tenant.id)
            previous = sub.status if sub is not None else None
            SubscriptionService.refresh_status(sub, now=now, persist=True)
            if sub is not None and sub.status != previous:
                dirty = True
            rows.append(
                {
                    "id": tenant.id,
                    "business_name": tenant.business_name,
                    "name": tenant.name,
                    "email": tenant.email,
                    "tenant_status": tenant.status,
                    "subscription": SubscriptionService.serialize(sub, now=now),
                }
            )
        if persist and dirty:
            db.session.commit()
        return rows

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
        old = _subscription_snapshot(row)
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
        PlatformAuditService.log(
            action=ACTION_SUBSCRIPTION_UPDATED,
            entity_type="SUBSCRIPTION",
            entity_id=row.id,
            tenant_id=tenant.id,
            old_data=old,
            new_data={**_subscription_snapshot(row), "operation": "assign_plan"},
        )
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def start_or_extend_trial(tenant_id: str, *, days: int):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        duration = _days(days, label="Trial duration")
        now = utc_now_naive()
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        old = _subscription_snapshot(row)
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
        PlatformAuditService.log(
            action=ACTION_SUBSCRIPTION_UPDATED,
            entity_type="SUBSCRIPTION",
            entity_id=row.id,
            tenant_id=tenant.id,
            old_data=old,
            new_data={**_subscription_snapshot(row), "operation": "extend_trial"},
        )
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
        old = _subscription_snapshot(row)
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
        PlatformAuditService.log(
            action=ACTION_SUBSCRIPTION_UPDATED,
            entity_type="SUBSCRIPTION",
            entity_id=row.id,
            tenant_id=tenant.id,
            old_data=old,
            new_data={**_subscription_snapshot(row), "operation": "renew"},
        )
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def cancel(tenant_id: str):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        if row is None:
            raise NotFoundError("Subscription not found")
        old = _subscription_snapshot(row)
        row.status = SUBSCRIPTION_CANCELLED
        row.ends_at = utc_now_naive()
        PlatformAuditService.log(
            action=ACTION_SUBSCRIPTION_UPDATED,
            entity_type="SUBSCRIPTION",
            entity_id=row.id,
            tenant_id=tenant.id,
            old_data=old,
            new_data={**_subscription_snapshot(row), "operation": "cancel"},
        )
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def access_counts(*, now=None) -> dict:
        now = now or utc_now_naive()
        tenant_ids = TenantRepository.list_ids()
        current = SubscriptionRepository.map_current_for_tenants(tenant_ids)
        expiring = 0
        expired = 0
        dirty = False
        for row in current.values():
            previous = row.status
            data = SubscriptionService.serialize(row, now=now)
            if data and data["is_expiring"]:
                expiring += 1
            SubscriptionService.refresh_status(row, now=now, persist=True)
            if row.status != previous:
                dirty = True
            if row.status == SUBSCRIPTION_EXPIRED:
                expired += 1
        if dirty:
            db.session.commit()
        return {"expiring_soon": expiring, "expired_subscriptions": expired}

    @staticmethod
    def count_expiring(*, now=None) -> int:
        return int(SubscriptionService.access_counts(now=now)["expiring_soon"])

    @staticmethod
    def count_expired(*, now=None) -> int:
        return int(SubscriptionService.access_counts(now=now)["expired_subscriptions"])
