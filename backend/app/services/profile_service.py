"""Authenticated user profile operations."""

from flask import current_app

from app.extensions import db
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.utils.exceptions import ConflictError, ValidationError
from app.utils.request_context import require_request_context


class ProfileService:
    @staticmethod
    def get_profile():
        ctx = require_request_context()
        user = UserRepository.get_by_id(ctx.user_id)
        return AuthService.serialize_user(user)

    @staticmethod
    def update_profile(*, name: str | None = None, phone: str | None = None):
        """Update personal profile fields. Phone is stored on tenant for owners."""
        ctx = require_request_context()
        user = UserRepository.get_by_id(ctx.user_id)
        old = AuthService.serialize_user(user)

        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationError("Name is required")
            user.name = name

        if phone is not None and user.tenant:
            user.tenant.phone = phone.strip() or None

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_PROFILE",
            entity_type="USER",
            entity_id=user.id,
            old_data=old,
            new_data=AuthService.serialize_user(user),
        )
        db.session.commit()
        return AuthService.serialize_user(user)

    @staticmethod
    def request_email_change(new_email: str):
        ctx = require_request_context()
        user = UserRepository.get_by_id(ctx.user_id)
        email_norm = (new_email or "").strip().lower()
        if not email_norm or "@" not in email_norm:
            raise ValidationError("A valid email is required")
        if email_norm == user.email.lower():
            raise ValidationError("New email must be different from the current email")

        existing = UserRepository.find_by_email(email_norm)
        if any(u.id != user.id for u in existing):
            raise ConflictError("Email is already in use")

        user.pending_email = email_norm
        raw_token = AuthService._issue_email_verification(
            user, purpose="email_change", new_email=email_norm
        )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="EMAIL_CHANGE_REQUESTED",
            entity_type="USER",
            entity_id=user.id,
            new_data={"pending_email": email_norm},
        )
        db.session.commit()

        verify_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={raw_token}"
        EmailService.send_verification_email(
            to=email_norm, name=user.name, verify_url=verify_url
        )

        result = {
            "message": "Verification email sent to the new address.",
            "pending_email": email_norm,
        }
        if current_app.config.get("ALLOW_DEV_AUTH_TOKENS"):
            result["verification_token"] = raw_token
        return result
