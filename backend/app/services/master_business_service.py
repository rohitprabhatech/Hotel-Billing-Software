"""Master-operated tenant activate / deactivate / subscription suspend."""

from app.extensions import db
from app.models.platform_audit_log import (
    ACTION_BUSINESS_ACTIVATED,
    ACTION_BUSINESS_DEACTIVATED,
    ACTION_BUSINESS_SUSPENDED,
    ACTION_BUSINESS_UNSUSPENDED,
)
from app.models.subscription import SUBSCRIPTION_ACTIVE, SUBSCRIPTION_SUSPENDED, SUBSCRIPTION_TRIAL
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.platform_audit_service import PlatformAuditService
from app.services.platform_notification_service import PlatformNotificationService
from app.services.subscription_service import SubscriptionService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.request_context import require_master_context
from app.utils.tokens import utc_now_naive


class MasterBusinessService:
    @staticmethod
    def activate(tenant_id: str):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        previous = tenant.status
        tenant.status = "ACTIVE"
        PlatformAuditService.log(
            action=ACTION_BUSINESS_ACTIVATED,
            entity_type="TENANT",
            entity_id=tenant.id,
            tenant_id=tenant.id,
            old_data={"status": previous},
            new_data={"status": tenant.status, "business_name": tenant.business_name},
        )
        if previous != "ACTIVE":
            PlatformNotificationService.create(
                notification_type="BUSINESS_ACTIVATED",
                title="Business activated",
                message=f"{tenant.business_name} is active again.",
                entity_type="TENANT",
                entity_id=tenant.id,
            )
        db.session.commit()
        return SubscriptionService.get_business(tenant.id)

    @staticmethod
    def deactivate(tenant_id: str):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        previous = tenant.status
        tenant.status = "SUSPENDED"
        PlatformAuditService.log(
            action=ACTION_BUSINESS_DEACTIVATED,
            entity_type="TENANT",
            entity_id=tenant.id,
            tenant_id=tenant.id,
            old_data={"status": previous},
            new_data={"status": tenant.status, "business_name": tenant.business_name},
        )
        if previous != "SUSPENDED":
            PlatformNotificationService.create(
                notification_type="BUSINESS_DEACTIVATED",
                title="Business deactivated",
                message=f"{tenant.business_name} is deactivated. Data is retained; login is blocked.",
                entity_type="TENANT",
                entity_id=tenant.id,
            )
        db.session.commit()
        return SubscriptionService.get_business(tenant.id)

    @staticmethod
    def suspend_subscription(tenant_id: str):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        if row is None:
            raise NotFoundError("Subscription not found")
        previous = row.status
        row.status = SUBSCRIPTION_SUSPENDED
        PlatformAuditService.log(
            action=ACTION_BUSINESS_SUSPENDED,
            entity_type="SUBSCRIPTION",
            entity_id=row.id,
            tenant_id=tenant.id,
            old_data={"status": previous},
            new_data={"status": row.status, "business_name": tenant.business_name},
        )
        if previous != SUBSCRIPTION_SUSPENDED:
            PlatformNotificationService.create(
                notification_type="BUSINESS_SUSPENDED",
                title="Business billing suspended",
                message=f"{tenant.business_name} can still sign in, but billing is locked.",
                entity_type="TENANT",
                entity_id=tenant.id,
            )
        db.session.commit()
        return SubscriptionService.serialize(row)

    @staticmethod
    def unsuspend_subscription(tenant_id: str):
        require_master_context()
        tenant = SubscriptionService._require_tenant(tenant_id)
        row = SubscriptionRepository.get_current_for_tenant(tenant.id)
        if row is None:
            raise NotFoundError("Subscription not found")
        if row.status != SUBSCRIPTION_SUSPENDED:
            raise ValidationError("Only a suspended subscription can be resumed")
        previous = row.status
        now = utc_now_naive()
        if (
            row.trial_ends_at is not None
            and row.trial_ends_at > now
            and row.payment_status is None
        ):
            row.status = SUBSCRIPTION_TRIAL
        else:
            row.status = SUBSCRIPTION_ACTIVE
        SubscriptionService.refresh_status(row, persist=True)
        PlatformAuditService.log(
            action=ACTION_BUSINESS_UNSUSPENDED,
            entity_type="SUBSCRIPTION",
            entity_id=row.id,
            tenant_id=tenant.id,
            old_data={"status": previous},
            new_data={"status": row.status, "business_name": tenant.business_name},
        )
        db.session.commit()
        return SubscriptionService.serialize(row)
