"""Master Admin HTTP controllers."""

from flask import request

from app.repositories.master_admin_repository import MasterAdminRepository
from app.schemas.master_schemas import (
    assign_plan_schema,
    duration_schema,
    plan_status_schema,
    plan_update_schema,
    plan_write_schema,
    reject_registration_schema,
    renew_schema,
    update_trial_settings_schema,
)
from app.services.expiry_job_service import ExpiryJobService
from app.services.master_business_service import MasterBusinessService
from app.services.master_dashboard_service import MasterDashboardService
from app.services.plan_service import PlanService
from app.services.platform_audit_service import PlatformAuditService
from app.services.platform_notification_service import PlatformNotificationService
from app.services.platform_settings_service import PlatformSettingsService
from app.services.registration_request_service import RegistrationRequestService
from app.services.subscription_service import SubscriptionService
from app.utils.request_context import require_master_context
from app.utils.responses import success_response


def dashboard_summary():
    data = MasterDashboardService.summary()
    return success_response(data=data)


def list_registration_requests():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))
    data, meta = RegistrationRequestService.list_requests(
        status=request.args.get("status"),
        q=request.args.get("q"),
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_registration_request(request_id: str):
    data = RegistrationRequestService.get_request(request_id)
    return success_response(data=data)


def approve_registration_request(request_id: str):
    data = RegistrationRequestService.approve(request_id)
    return success_response(data=data)


def reject_registration_request(request_id: str):
    payload = reject_registration_schema.load(request.get_json() or {})
    data = RegistrationRequestService.reject(request_id, payload["reason"])
    return success_response(data=data)


def get_trial_settings():
    data = PlatformSettingsService.get_for_master()
    return success_response(data=data)


def update_trial_settings():
    payload = update_trial_settings_schema.load(request.get_json() or {})
    data = PlatformSettingsService.update(
        trial_enabled=payload["trial_enabled"],
        trial_days=payload["trial_days"],
        expiry_warning_days=payload.get("expiry_warning_days"),
    )
    return success_response(data=data)


def list_trials():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))
    data, meta = SubscriptionService.list_active_trials(page=page, per_page=per_page)
    return success_response(data=data, meta=meta)


def list_plans():
    include_inactive = str(request.args.get("include_inactive", "true")).lower() in {
        "1",
        "true",
        "yes",
    }
    data = PlanService.list_plans(include_inactive=include_inactive)
    return success_response(data=data)


def create_plan():
    payload = plan_write_schema.load(request.get_json() or {})
    data = PlanService.create(payload)
    return success_response(data=data, status_code=201)


def get_plan(plan_id: str):
    data = PlanService.get_plan(plan_id)
    return success_response(data=data)


def update_plan(plan_id: str):
    raw = request.get_json() or {}
    loaded = plan_update_schema.load(raw)
    payload = {key: loaded[key] for key in raw if key in loaded}
    data = PlanService.update(plan_id, payload)
    return success_response(data=data)


def set_plan_status(plan_id: str):
    payload = plan_status_schema.load(request.get_json() or {})
    data = PlanService.set_active(plan_id, payload["is_active"])
    return success_response(data=data)


def list_businesses():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))
    data, meta = SubscriptionService.list_businesses(
        status=request.args.get("status"),
        tenant_status=request.args.get("tenant_status"),
        q=request.args.get("q"),
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def list_expiring():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))
    data, meta = SubscriptionService.list_expiring(page=page, per_page=per_page)
    return success_response(data=data, meta=meta)


def get_business(tenant_id: str):
    data = SubscriptionService.get_business(tenant_id)
    return success_response(data=data)


def assign_plan(tenant_id: str):
    payload = assign_plan_schema.load(request.get_json() or {})
    data = SubscriptionService.assign_plan(
        tenant_id, plan_id=payload["plan_id"], days=payload.get("days")
    )
    return success_response(data=data)


def extend_trial(tenant_id: str):
    payload = duration_schema.load(request.get_json() or {})
    data = SubscriptionService.start_or_extend_trial(tenant_id, days=payload["days"])
    return success_response(data=data)


def renew_subscription(tenant_id: str):
    payload = renew_schema.load(request.get_json() or {})
    data = SubscriptionService.renew(
        tenant_id, days=payload["days"], plan_id=payload.get("plan_id")
    )
    return success_response(data=data)


def cancel_subscription(tenant_id: str):
    data = SubscriptionService.cancel(tenant_id)
    return success_response(data=data)


def activate_business(tenant_id: str):
    data = MasterBusinessService.activate(tenant_id)
    return success_response(data=data)


def deactivate_business(tenant_id: str):
    data = MasterBusinessService.deactivate(tenant_id)
    return success_response(data=data)


def suspend_business(tenant_id: str):
    data = MasterBusinessService.suspend_subscription(tenant_id)
    return success_response(data=data)


def unsuspend_business(tenant_id: str):
    data = MasterBusinessService.unsuspend_subscription(tenant_id)
    return success_response(data=data)


def list_audit_logs():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))
    data, meta = PlatformAuditService.list_logs(
        action=request.args.get("action"),
        entity_type=request.args.get("entity_type"),
        tenant_id=request.args.get("tenant_id"),
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def list_notifications():
    unread_only = str(request.args.get("unread_only", "")).lower() in {"1", "true", "yes"}
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = PlatformNotificationService.list_notifications(
        unread_only=unread_only,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def unread_notification_count():
    return success_response(data=PlatformNotificationService.unread_count())


def mark_notification_read(notification_id: str):
    return success_response(data=PlatformNotificationService.mark_read(notification_id))


def mark_all_notifications_read():
    return success_response(data=PlatformNotificationService.mark_all_read())


def run_expiry_check():
    data = ExpiryJobService.run()
    return success_response(data=data)


def me():
    ctx = require_master_context()
    admin = MasterAdminRepository.get_by_id(ctx.admin_id)
    from app.services.auth_service import AuthService

    return success_response(data=AuthService.serialize_master_admin(admin))
