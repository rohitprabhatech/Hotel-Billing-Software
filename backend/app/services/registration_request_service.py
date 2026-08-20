"""Public registration requests and Master Admin approve/reject."""

from flask import current_app

from app.constants.business_types import normalize_business_type
from app.extensions import db
from app.models.registration_request import (
    REGISTRATION_APPROVED,
    REGISTRATION_PENDING,
    REGISTRATION_REJECTED,
    REGISTRATION_STATUSES,
    RegistrationRequest,
)
from app.models.role import ROLE_OWNER
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.master_admin_repository import MasterAdminRepository
from app.repositories.registration_request_repository import RegistrationRequestRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.models.platform_audit_log import ACTION_BUSINESS_APPROVED, ACTION_BUSINESS_REJECTED
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from app.services.platform_audit_service import PlatformAuditService
from app.services.subscription_service import SubscriptionService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_master_context
from app.utils.security import hash_password
from app.utils.tokens import utc_now_naive


class RegistrationRequestService:
    @staticmethod
    def submit(payload: dict):
        business_name = (payload.get("business_name") or "").strip()
        display_name = (
            payload.get("name") or payload.get("hotel_name") or business_name or ""
        ).strip()
        if not business_name:
            business_name = display_name
        if not display_name:
            display_name = business_name

        owner_name = (payload.get("owner_name") or "").strip()
        owner_email = (payload.get("owner_email") or "").strip().lower()
        password = payload.get("password") or ""
        confirm = payload.get("confirm_password") or ""

        if not payload.get("terms_accepted"):
            raise ValidationError("You must agree to the Terms of Service and Privacy Policy")
        if not business_name:
            raise ValidationError("Business name is required")
        if not owner_name:
            raise ValidationError("Owner name is required")
        if not owner_email or "@" not in owner_email:
            raise ValidationError("A valid owner email is required")
        if password != confirm:
            raise ValidationError("Password and confirm password do not match")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        try:
            business_type = normalize_business_type(payload.get("business_type"))
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        RegistrationRequestService._assert_email_available(owner_email)

        row = RegistrationRequest(
            id=new_uuid(),
            business_name=business_name,
            business_type=business_type,
            owner_name=owner_name,
            owner_email=owner_email,
            password_hash=hash_password(password),
            mobile=(payload.get("mobile") or payload.get("phone") or "").strip() or None,
            address=(payload.get("address") or "").strip() or None,
            city=(payload.get("city") or "").strip() or None,
            state=(payload.get("state") or "").strip() or None,
            country=(payload.get("country") or "India").strip() or "India",
            pincode=(payload.get("pincode") or "").strip() or None,
            gst_number=(payload.get("gst_number") or "").strip() or None,
            fssai_number=(payload.get("fssai_number") or "").strip() or None,
            status=REGISTRATION_PENDING,
            requested_at=utc_now_naive(),
            terms_accepted_at=utc_now_naive(),
        )
        RegistrationRequestRepository.add(row)
        db.session.commit()

        try:
            EmailService.send_registration_received_email(
                to=owner_email, name=owner_name, business_name=business_name
            )
        except Exception:  # noqa: BLE001
            current_app.logger.exception("Failed to send registration received email")

        return {
            "message": (
                "Your registration request has been submitted successfully. "
                "Your account will be activated after approval by Prabha Technology."
            ),
            "request_id": row.id,
            "status": row.status,
            "owner_email": row.owner_email,
            "business_name": row.business_name,
            "business_type": row.business_type,
        }

    @staticmethod
    def list_requests(*, status=None, q=None, page=1, per_page=25):
        require_master_context()
        status_norm = None
        if status:
            status_norm = str(status).strip().upper()
            if status_norm not in REGISTRATION_STATUSES:
                raise ValidationError("Invalid registration status filter")
        rows, total = RegistrationRequestRepository.list_filtered(
            status=status_norm,
            q=q,
            page=page,
            per_page=per_page,
        )
        return (
            [RegistrationRequestService.serialize(r) for r in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 25), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_request(request_id: str):
        require_master_context()
        row = RegistrationRequestRepository.get_by_id(request_id)
        if row is None:
            raise NotFoundError("Registration request not found")
        return RegistrationRequestService.serialize(row, detail=True)

    @staticmethod
    def approve(request_id: str):
        ctx = require_master_context()
        row = RegistrationRequestRepository.get_by_id(request_id)
        if row is None:
            raise NotFoundError("Registration request not found")
        if row.status != REGISTRATION_PENDING:
            raise ValidationError("Only pending requests can be approved")

        RegistrationRequestService._assert_email_available(row.owner_email, ignore_request_id=row.id)

        owner_role = RoleRepository.get_by_name(ROLE_OWNER)
        if owner_role is None:
            raise ValidationError("Owner role is not configured")

        tenant = Tenant(
            id=new_uuid(),
            name=row.business_name,
            business_name=row.business_name,
            business_type=row.business_type,
            address=row.address,
            city=row.city,
            state=row.state,
            pincode=row.pincode,
            phone=row.mobile,
            email=row.owner_email,
            gst_number=row.gst_number,
            fssai_number=row.fssai_number,
            status="ACTIVE",
        )
        db.session.add(tenant)
        db.session.flush()

        owner = User(
            id=new_uuid(),
            tenant_id=tenant.id,
            role_id=owner_role.id,
            name=row.owner_name,
            email=row.owner_email,
            password_hash=row.password_hash,
            is_active=True,
            email_verified=True,
            token_version=0,
        )
        db.session.add(owner)
        db.session.flush()

        now = utc_now_naive()
        row.status = REGISTRATION_APPROVED
        row.approved_at = now
        row.approved_by = ctx.admin_id
        row.tenant_id = tenant.id

        trial = SubscriptionService.start_trial_for_new_tenant(tenant)

        AuditService.log(
            tenant_id=tenant.id,
            action="REGISTER_BUSINESS",
            entity_type="TENANT",
            entity_id=tenant.id,
            user_id=owner.id,
            user_name=owner.name,
            new_data={
                "name": tenant.name,
                "business_name": tenant.business_name,
                "business_type": tenant.business_type,
                "owner_email": owner.email,
                "approved_by": ctx.admin_id,
                "trial_status": trial.status if trial else None,
                "trial_days": (
                    SubscriptionService.remaining_days(trial.trial_ends_at) if trial else None
                ),
            },
        )
        PlatformAuditService.log(
            action=ACTION_BUSINESS_APPROVED,
            entity_type="REGISTRATION_REQUEST",
            entity_id=row.id,
            tenant_id=tenant.id,
            new_data={
                "business_name": tenant.business_name,
                "owner_email": owner.email,
                "tenant_id": tenant.id,
                "trial_status": trial.status if trial else None,
            },
        )
        db.session.commit()

        login_url = f"{current_app.config['FRONTEND_URL']}/login"
        try:
            EmailService.send_registration_approved_email(
                to=owner.email,
                name=owner.name,
                business_name=tenant.business_name,
                login_url=login_url,
                trial_days=(
                    (trial.trial_ends_at.date() - trial.trial_starts_at.date()).days
                    if trial and trial.trial_starts_at and trial.trial_ends_at
                    else None
                ),
                trial_ends_at=trial.trial_ends_at.date().isoformat() if trial and trial.trial_ends_at else None,
            )
        except Exception:  # noqa: BLE001
            current_app.logger.exception("Failed to send registration approved email")

        data = RegistrationRequestService.serialize(row, detail=True)
        data["subscription"] = SubscriptionService.serialize(trial)
        return data

    @staticmethod
    def reject(request_id: str, reason: str):
        ctx = require_master_context()
        reason = (reason or "").strip()
        if len(reason) < 8:
            raise ValidationError("A rejection reason is required (at least 8 characters)")

        row = RegistrationRequestRepository.get_by_id(request_id)
        if row is None:
            raise NotFoundError("Registration request not found")
        if row.status != REGISTRATION_PENDING:
            raise ValidationError("Only pending requests can be rejected")

        now = utc_now_naive()
        row.status = REGISTRATION_REJECTED
        row.rejected_at = now
        row.rejected_by = ctx.admin_id
        row.rejection_reason = reason
        PlatformAuditService.log(
            action=ACTION_BUSINESS_REJECTED,
            entity_type="REGISTRATION_REQUEST",
            entity_id=row.id,
            new_data={
                "business_name": row.business_name,
                "owner_email": row.owner_email,
                "reason": reason,
            },
        )
        db.session.commit()

        try:
            EmailService.send_registration_rejected_email(
                to=row.owner_email,
                name=row.owner_name,
                business_name=row.business_name,
                reason=reason,
            )
        except Exception:  # noqa: BLE001
            current_app.logger.exception("Failed to send registration rejected email")

        return RegistrationRequestService.serialize(row, detail=True)

    @staticmethod
    def _assert_email_available(email: str, *, ignore_request_id: str | None = None):
        if UserRepository.find_by_email(email) or MasterAdminRepository.find_by_email(email):
            raise ConflictError("An account with this email already exists")
        pending = RegistrationRequestRepository.find_pending_by_email(email)
        if pending is not None and pending.id != ignore_request_id:
            raise ConflictError("A registration request with this email is already pending")

    @staticmethod
    def serialize(row: RegistrationRequest, *, detail: bool = False) -> dict:
        data = {
            "id": row.id,
            "business_name": row.business_name,
            "business_type": row.business_type,
            "owner_name": row.owner_name,
            "owner_email": row.owner_email,
            "mobile": row.mobile,
            "status": row.status,
            "requested_at": row.requested_at.isoformat() if row.requested_at else None,
            "approved_at": row.approved_at.isoformat() if row.approved_at else None,
            "rejected_at": row.rejected_at.isoformat() if row.rejected_at else None,
            "tenant_id": row.tenant_id,
        }
        if detail:
            data.update(
                {
                    "address": row.address,
                    "city": row.city,
                    "state": row.state,
                    "country": row.country,
                    "pincode": row.pincode,
                    "gst_number": row.gst_number,
                    "fssai_number": row.fssai_number,
                    "rejection_reason": row.rejection_reason,
                    "terms_accepted_at": (
                        row.terms_accepted_at.isoformat() if row.terms_accepted_at else None
                    ),
                }
            )
        return data
