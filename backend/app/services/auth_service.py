"""Authentication business logic."""

from datetime import datetime, timezone

from flask import current_app
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import UnauthorizedError, ValidationError
from app.utils.security import verify_password


class AuthService:
    @staticmethod
    def login(email: str, password: str, ip_address: str | None, user_agent: str | None):
        if not email or not password:
            raise ValidationError("Email and password are required")

        candidates = UserRepository.find_by_email(email)
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

        matched.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
        access_token = create_access_token(
            identity=matched.id,
            additional_claims={
                "tenant_id": matched.tenant_id,
                "role": matched.role_name,
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

        expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": int(expires.total_seconds()),
            "user": AuthService.serialize_user(matched),
        }

    @staticmethod
    def logout(user, ip_address: str | None, user_agent: str | None):
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
    def me(user):
        return AuthService.serialize_user(user)

    @staticmethod
    def serialize_user(user):
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role_name,
            "is_active": user.is_active,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "tenant": {
                "id": user.tenant.id,
                "name": user.tenant.name,
                "business_name": user.tenant.business_name,
                "status": user.tenant.status,
            },
        }