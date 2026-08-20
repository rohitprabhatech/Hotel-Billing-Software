"""Master dashboard — real tenant counts only (no invented KPIs)."""

from app.models.registration_request import REGISTRATION_PENDING
from app.repositories.registration_request_repository import RegistrationRequestRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.subscription_service import SubscriptionService
from app.utils.request_context import require_master_context
from app.utils.tokens import utc_now_naive


class MasterDashboardService:
    @staticmethod
    def summary():
        require_master_context()
        now = utc_now_naive()
        counts = SubscriptionService.access_counts(now=now)
        return {
            "total_businesses": TenantRepository.count_all(),
            "active_businesses": TenantRepository.count_by_status("ACTIVE"),
            "suspended_businesses": TenantRepository.count_by_status("SUSPENDED"),
            "pending_requests": RegistrationRequestRepository.count_by_status(
                REGISTRATION_PENDING
            ),
            "trial_businesses": SubscriptionRepository.count_active_trials(now=now),
            "expiring_soon": counts["expiring_soon"],
            "expired_subscriptions": counts["expired_subscriptions"],
        }
