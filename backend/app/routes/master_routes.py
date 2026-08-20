"""Master Admin routes — platform operators only."""

from flask import Blueprint

from app.controllers import master_controller
from app.middleware.auth import master_required

master_bp = Blueprint("master", __name__, url_prefix="/master")


@master_bp.get("/dashboard/summary")
@master_required
def dashboard_summary():
    return master_controller.dashboard_summary()


@master_bp.get("/registration-requests")
@master_required
def list_registration_requests():
    return master_controller.list_registration_requests()


@master_bp.get("/registration-requests/<request_id>")
@master_required
def get_registration_request(request_id):
    return master_controller.get_registration_request(request_id)


@master_bp.post("/registration-requests/<request_id>/approve")
@master_required
def approve_registration_request(request_id):
    return master_controller.approve_registration_request(request_id)


@master_bp.post("/registration-requests/<request_id>/reject")
@master_required
def reject_registration_request(request_id):
    return master_controller.reject_registration_request(request_id)


@master_bp.get("/settings/trial")
@master_required
def get_trial_settings():
    return master_controller.get_trial_settings()


@master_bp.put("/settings/trial")
@master_required
def update_trial_settings():
    return master_controller.update_trial_settings()


@master_bp.get("/trials")
@master_required
def list_trials():
    return master_controller.list_trials()


@master_bp.get("/plans")
@master_required
def list_plans():
    return master_controller.list_plans()


@master_bp.post("/plans")
@master_required
def create_plan():
    return master_controller.create_plan()


@master_bp.get("/plans/<plan_id>")
@master_required
def get_plan(plan_id):
    return master_controller.get_plan(plan_id)


@master_bp.put("/plans/<plan_id>")
@master_required
def update_plan(plan_id):
    return master_controller.update_plan(plan_id)


@master_bp.patch("/plans/<plan_id>/status")
@master_required
def set_plan_status(plan_id):
    return master_controller.set_plan_status(plan_id)


@master_bp.get("/businesses")
@master_required
def list_businesses():
    return master_controller.list_businesses()


@master_bp.get("/businesses/expiring")
@master_required
def list_expiring_businesses():
    return master_controller.list_expiring()


@master_bp.get("/businesses/<tenant_id>")
@master_required
def get_business(tenant_id):
    return master_controller.get_business(tenant_id)


@master_bp.post("/businesses/<tenant_id>/assign-plan")
@master_required
def assign_plan(tenant_id):
    return master_controller.assign_plan(tenant_id)


@master_bp.post("/businesses/<tenant_id>/extend-trial")
@master_required
def extend_trial(tenant_id):
    return master_controller.extend_trial(tenant_id)


@master_bp.post("/businesses/<tenant_id>/renew")
@master_required
def renew_subscription(tenant_id):
    return master_controller.renew_subscription(tenant_id)


@master_bp.post("/businesses/<tenant_id>/cancel-subscription")
@master_required
def cancel_subscription(tenant_id):
    return master_controller.cancel_subscription(tenant_id)


@master_bp.post("/businesses/<tenant_id>/activate")
@master_required
def activate_business(tenant_id):
    return master_controller.activate_business(tenant_id)


@master_bp.post("/businesses/<tenant_id>/deactivate")
@master_required
def deactivate_business(tenant_id):
    return master_controller.deactivate_business(tenant_id)


@master_bp.post("/businesses/<tenant_id>/suspend")
@master_required
def suspend_business(tenant_id):
    return master_controller.suspend_business(tenant_id)


@master_bp.post("/businesses/<tenant_id>/unsuspend")
@master_required
def unsuspend_business(tenant_id):
    return master_controller.unsuspend_business(tenant_id)


@master_bp.get("/audit-logs")
@master_required
def list_audit_logs():
    return master_controller.list_audit_logs()


@master_bp.get("/notifications")
@master_required
def list_notifications():
    return master_controller.list_notifications()


@master_bp.get("/notifications/unread-count")
@master_required
def unread_notification_count():
    return master_controller.unread_notification_count()


@master_bp.patch("/notifications/<notification_id>/read")
@master_required
def mark_notification_read(notification_id):
    return master_controller.mark_notification_read(notification_id)


@master_bp.patch("/notifications/read-all")
@master_required
def mark_all_notifications_read():
    return master_controller.mark_all_notifications_read()


@master_bp.post("/jobs/expiry-check")
@master_required
def run_expiry_check():
    return master_controller.run_expiry_check()
