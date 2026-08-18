"""Authentication business logic."""

from flask import current_app
from flask_jwt_extended import create_access_token

from app.constants.business_types import business_type_label
from app.extensions import db
from app.models.auth_token import EmailVerificationToken, PasswordResetToken
from app.models.master_admin import ROLE_MASTER_ADMIN, MasterAdmin
from app.models.user import User
from app.repositories.master_admin_repository import MasterAdminRepository
from app.repositories.registration_request_repository import RegistrationRequestRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.email_service import EmailService
from app.services.subscription_service import SubscriptionService
from app.utils.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.utils.ids import new_uuid
from app.utils.security import hash_password, verify_password
from app.utils.tokens import expires_at, generate_token, hash_token, utc_now_naive


class AuthService:
    @staticmethod
    def login(email: str, password: str, ip_address: str | None, user_agent: str | None):
        if not email or not password:
            raise ValidationError("Email and password are required")

        candidates = UserRepository.find_by_email(email)
        if candidates:
            matched = None
            for user in candidates:
                if not user.is_active:
                    continue
                if not user.tenant or not user.tenant.is_active():
                    continue
                if verify_password(user.password_hash, password):
                    matched = user
                    break

            if matched is None:
                raise UnauthorizedError("Invalid email or password")

            if current_app.config.get("EMAIL_VERIFICATION_REQUIRED") and not matched.email_verified:
                raise UnauthorizedError(
                    "Email not verified. Please verify your email before signing in."
                )

            matched.last_login_at = utc_now_naive()
            access_token = create_access_token(
                identity=matched.id,
                additional_claims={
                    "tenant_id": matched.tenant_id,
                    "role": matched.role_name,
                    "tv": matched.token_version or 0,
                },
            )

            AuditService.log(
                tenant_id=matched.tenant_id,
                action="LOGIN",
                entity_type="AUTH",
                entity_id=matched.id,
                user_id=matched.id,
                user_name=matched.name,
                new_data={"email": matched.email, "role": matched.role_name},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.session.commit()

            if current_app.config.get("SEND_LOGIN_NOTIFICATIONS"):
                try:
                    EmailService.send_login_notification(
                        to=matched.email, name=matched.name, ip_address=ip_address
                    )
                except Exception:  # noqa: BLE001 — login must not fail on mail
                    current_app.logger.exception("Failed to send login notification")

            expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": int(expires.total_seconds()),
                "user": AuthService.serialize_user(matched),
            }

        admin = MasterAdminRepository.find_by_email(email)
        if admin is not None and admin.is_active and verify_password(admin.password_hash, password):
            admin.last_login_at = utc_now_naive()
            access_token = create_access_token(
                identity=admin.id,
                additional_claims={
                    "role": ROLE_MASTER_ADMIN,
                    "tv": admin.token_version or 0,
                },
            )
            db.session.commit()

            expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": int(expires.total_seconds()),
                "user": AuthService.serialize_master_admin(admin),
            }

        pending = RegistrationRequestRepository.find_pending_by_email(email)
        if pending is not None and verify_password(pending.password_hash, password):
            raise UnauthorizedError(
                "Your registration request is pending approval by Prabha Technology."
            )

        raise UnauthorizedError("Invalid email or password")

    @staticmethod
    def logout(user, ip_address: str | None, user_agent: str | None):
        # Revoke outstanding JWTs for this user (token_version claim must match).
        user.token_version = int(user.token_version or 0) + 1
        AuditService.log(
            tenant_id=user.tenant_id,
            action="LOGOUT",
            entity_type="AUTH",
            entity_id=user.id,
            user_id=user.id,
            user_name=user.name,
            ip_address=ip_address,
            user_agent=user_agent,
            commit=True,
        )
        return {"message": "Logged out successfully"}

    @staticmethod
    def logout_master(admin: MasterAdmin):
        admin.token_version = int(admin.token_version or 0) + 1
        db.session.commit()
        return {"message": "Logged out successfully"}

    @staticmethod
    def me(user):
        return AuthService.serialize_user(user)

    @staticmethod
    def register_business(payload: dict):
        from app.services.registration_request_service import RegistrationRequestService

        return RegistrationRequestService.submit(payload)

    @staticmethod
    def register_hotel(payload: dict):
        """Legacy alias for register_business."""
        return AuthService.register_business(payload)

    @staticmethod
    def verify_email(token: str):
        if not token:
            raise ValidationError("Verification token is required")

        record = (
            db.session.query(EmailVerificationToken)
            .filter(EmailVerificationToken.token_hash == hash_token(token))
            .first()
        )
        if record is None or record.verified_at is not None:
            raise ValidationError("Invalid or already used verification token")
        if record.expires_at < utc_now_naive():
            raise ValidationError("Verification token has expired")

        user = UserRepository.get_by_id(record.user_id)
        if user is None or not user.is_active:
            raise ValidationError("User account is not available")

        if record.purpose == "email_change" and record.new_email:
            new_email = record.new_email.strip().lower()
            existing = UserRepository.find_by_email(new_email)
            if any(u.id != user.id for u in existing):
                raise ConflictError("Email is already in use")
            old_email = user.email
            user.email = new_email
            user.pending_email = None
            AuditService.log(
                tenant_id=user.tenant_id,
                action="EMAIL_CHANGED",
                entity_type="USER",
                entity_id=user.id,
                user_id=user.id,
                user_name=user.name,
                old_data={"email": old_email},
                new_data={"email": new_email},
            )
        else:
            AuditService.log(
                tenant_id=user.tenant_id,
                action="EMAIL_VERIFIED",
                entity_type="USER",
                entity_id=user.id,
                user_id=user.id,
                user_name=user.name,
                new_data={"email": user.email},
            )

        user.email_verified = True
        user.email_verified_at = utc_now_naive()
        record.verified_at = utc_now_naive()
        AuthService._invalidate_unused_email_verification_tokens(
            user.id, purpose=record.purpose, except_id=record.id
        )
        db.session.commit()
        return {"message": "Email verified successfully. You can now sign in."}

    @staticmethod
    def resend_verification(email: str):
        email_norm = (email or "").strip().lower()
        if not email_norm:
            raise ValidationError("Email is required")

        users = UserRepository.find_by_email(email_norm)
        # Always return generic success to avoid account enumeration
        if not users:
            return {"message": "If the account exists, a verification email has been sent."}

        user = users[0]
        if user.email_verified and not user.pending_email:
            return {"message": "If the account exists, a verification email has been sent."}

        purpose = "email_change" if user.pending_email else "signup"
        raw_token = AuthService._issue_email_verification(
            user, purpose=purpose, new_email=user.pending_email
        )
        db.session.commit()
        verify_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={raw_token}"
        EmailService.send_verification_email(
            to=user.pending_email or user.email, name=user.name, verify_url=verify_url
        )
        result = {"message": "If the account exists, a verification email has been sent."}
        if current_app.config.get("ALLOW_DEV_AUTH_TOKENS"):
            result["verification_token"] = raw_token
        return result

    @staticmethod
    def forgot_password(email: str):
        email_norm = (email or "").strip().lower()
        if not email_norm:
            raise ValidationError("Email is required")

        users = UserRepository.find_by_email(email_norm)
        result = {"message": "If the account exists, a password reset email has been sent."}
        if not users:
            return result

        user = next((u for u in users if u.is_active), None)
        if user is None:
            return result

        AuthService._invalidate_unused_password_reset_tokens(user.id)
        raw_token = generate_token()
        db.session.add(
            PasswordResetToken(
                id=new_uuid(),
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=expires_at(hours=1),
            )
        )
        AuditService.log(
            tenant_id=user.tenant_id,
            action="PASSWORD_RESET_REQUESTED",
            entity_type="AUTH",
            entity_id=user.id,
            user_id=user.id,
            user_name=user.name,
            new_data={"email": user.email},
        )
        db.session.commit()

        reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={raw_token}"
        EmailService.send_password_reset_email(
            to=user.email, name=user.name, reset_url=reset_url
        )
        if current_app.config.get("ALLOW_DEV_AUTH_TOKENS"):
            result["reset_token"] = raw_token
        return result

    @staticmethod
    def reset_password(token: str, password: str, confirm_password: str):
        if not token:
            raise ValidationError("Reset token is required")
        if password != confirm_password:
            raise ValidationError("Password and confirm password do not match")
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        record = (
            db.session.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == hash_token(token))
            .first()
        )
        if record is None or record.used_at is not None:
            raise ValidationError("Invalid or already used reset token")
        if record.expires_at < utc_now_naive():
            raise ValidationError("Reset token has expired")

        user = UserRepository.get_by_id(record.user_id)
        if user is None or not user.is_active:
            raise ValidationError("User account is not available")

        AuthService._set_password(user, password)
        record.used_at = utc_now_naive()
        AuthService._invalidate_unused_password_reset_tokens(user.id, except_id=record.id)
        AuditService.log(
            tenant_id=user.tenant_id,
            action="PASSWORD_CHANGED",
            entity_type="AUTH",
            entity_id=user.id,
            user_id=user.id,
            user_name=user.name,
            new_data={"via": "reset_token"},
        )
        db.session.commit()

        try:
            EmailService.send_password_changed_email(to=user.email, name=user.name)
        except Exception:  # noqa: BLE001
            current_app.logger.exception("Failed to send password changed email")

        return {"message": "Password updated successfully. You can now sign in."}

    @staticmethod
    def change_password(user, *, current_password: str, new_password: str, confirm_password: str):
        if not current_password or not new_password:
            raise ValidationError("Current and new password are required")
        if new_password != confirm_password:
            raise ValidationError("Password and confirm password do not match")
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not verify_password(user.password_hash, current_password):
            raise ValidationError("Current password is incorrect")
        if current_password == new_password:
            raise ValidationError("New password must be different from the current password")

        AuthService._set_password(user, new_password)
        AuditService.log(
            tenant_id=user.tenant_id,
            action="PASSWORD_CHANGED",
            entity_type="AUTH",
            entity_id=user.id,
            user_id=user.id,
            user_name=user.name,
            new_data={"via": "change_password"},
        )
        db.session.commit()

        try:
            EmailService.send_password_changed_email(to=user.email, name=user.name)
        except Exception:  # noqa: BLE001
            current_app.logger.exception("Failed to send password changed email")

        return {
            "message": "Password updated successfully. Please sign in again.",
            "require_relogin": True,
        }

    @staticmethod
    def change_master_password(
        admin: MasterAdmin, current_password: str, new_password: str, confirm_password: str
    ):
        if new_password != confirm_password:
            raise ValidationError("Password and confirm password do not match")
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not verify_password(admin.password_hash, current_password):
            raise ValidationError("Current password is incorrect")
        if current_password == new_password:
            raise ValidationError("New password must be different from the current password")

        admin.password_hash = hash_password(new_password)
        admin.token_version = int(admin.token_version or 0) + 1
        db.session.commit()
        return {
            "message": "Password updated successfully. Please sign in again.",
            "require_relogin": True,
        }

    @staticmethod
    def _set_password(user: User, password: str):
        user.password_hash = hash_password(password)
        user.password_changed_at = utc_now_naive()
        user.token_version = int(user.token_version or 0) + 1

    @staticmethod
    def _invalidate_unused_password_reset_tokens(user_id: str, *, except_id: str | None = None):
        now = utc_now_naive()
        query = db.session.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
        if except_id:
            query = query.filter(PasswordResetToken.id != except_id)
        query.update({PasswordResetToken.used_at: now}, synchronize_session=False)

    @staticmethod
    def _invalidate_unused_email_verification_tokens(
        user_id: str, *, purpose: str, except_id: str | None = None
    ):
        now = utc_now_naive()
        query = db.session.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.purpose == purpose,
            EmailVerificationToken.verified_at.is_(None),
        )
        if except_id:
            query = query.filter(EmailVerificationToken.id != except_id)
        query.update(
            {EmailVerificationToken.verified_at: now},
            synchronize_session=False,
        )

    @staticmethod
    def _issue_email_verification(
        user: User, *, purpose: str = "signup", new_email: str | None = None
    ) -> str:
        AuthService._invalidate_unused_email_verification_tokens(user.id, purpose=purpose)
        raw_token = generate_token()
        db.session.add(
            EmailVerificationToken(
                id=new_uuid(),
                user_id=user.id,
                token_hash=hash_token(raw_token),
                purpose=purpose,
                new_email=new_email,
                expires_at=expires_at(hours=24),
            )
        )
        return raw_token

    @staticmethod
    def serialize_user(user):
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role_name,
            "is_active": user.is_active,
            "email_verified": bool(user.email_verified),
            "pending_email": user.pending_email,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "tenant": {
                "id": user.tenant.id,
                "name": user.tenant.name,
                "business_name": user.tenant.business_name,
                "business_type": user.tenant.business_type or "other",
                "business_type_label": business_type_label(user.tenant.business_type),
                "status": user.tenant.status,
                "subscription": SubscriptionService.serialize_for_tenant(user.tenant_id),
            },
        }

    @staticmethod
    def serialize_master_admin(admin: MasterAdmin):
        return {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "role": ROLE_MASTER_ADMIN,
            "is_active": admin.is_active,
            "email_verified": True,
            "pending_email": None,
            "last_login_at": admin.last_login_at.isoformat() if admin.last_login_at else None,
            "tenant": None,
        }
