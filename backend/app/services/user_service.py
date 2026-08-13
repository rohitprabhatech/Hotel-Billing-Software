"""Owner-managed billing user operations."""

from app.extensions import db
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_request_context
from app.utils.security import hash_password


class UserService:
    @staticmethod
    def list_users():
        ctx = require_request_context()
        users = UserRepository.list_by_tenant(ctx.tenant_id)
        return [UserService.serialize(u) for u in users]

    @staticmethod
    def get_user(user_id: str):
        ctx = require_request_context()
        user = UserRepository.get_by_id_and_tenant(user_id, ctx.tenant_id)
        if user is None:
            raise NotFoundError("User not found")
        return UserService.serialize(user)

    @staticmethod
    def create_billing_user(*, name: str, email: str, password: str):
        ctx = require_request_context()
        UserService._validate_user_payload(name, email, password, require_password=True)

        if UserRepository.find_by_tenant_and_email(ctx.tenant_id, email):
            raise ConflictError("A user with this email already exists for this hotel")

        role = RoleRepository.get_by_name(ROLE_BILLING_USER)
        if role is None:
            raise ValidationError("Billing user role is not configured")

        user = User(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            role_id=role.id,
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=hash_password(password),
            is_active=True,
        )
        UserRepository.add(user)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_USER",
            entity_type="USER",
            entity_id=user.id,
            new_data={
                "name": user.name,
                "email": user.email,
                "role": ROLE_BILLING_USER,
                "is_active": True,
            },
        )
        db.session.commit()
        return UserService.serialize(user)

    @staticmethod
    def update_user(user_id: str, *, name: str | None, email: str | None, is_active: bool | None):
        ctx = require_request_context()
        user = UserRepository.get_by_id_and_tenant(user_id, ctx.tenant_id)
        if user is None:
            raise NotFoundError("User not found")

        if user.id == ctx.user_id and is_active is False:
            raise ValidationError("You cannot deactivate your own account")

        old = UserService.serialize(user)

        if name is not None:
            if not name.strip():
                raise ValidationError("Name is required")
            user.name = name.strip()

        if email is not None:
            email_norm = email.strip().lower()
            if not email_norm or "@" not in email_norm:
                raise ValidationError("A valid email is required")
            existing = UserRepository.find_by_tenant_and_email(ctx.tenant_id, email_norm)
            if existing and existing.id != user.id:
                raise ConflictError("A user with this email already exists for this hotel")
            user.email = email_norm

        if is_active is not None:
            # Owners should not demote/deactivate another owner in v1 via this API casually.
            if user.role_name == ROLE_OWNER and user.id != ctx.user_id and is_active is False:
                raise ForbiddenError("Cannot deactivate another owner account")
            user.is_active = bool(is_active)

        action = "DEACTIVATE_USER" if old["is_active"] and not user.is_active else "UPDATE_USER"
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action=action,
            entity_type="USER",
            entity_id=user.id,
            old_data=old,
            new_data=UserService.serialize(user),
        )
        db.session.commit()
        return UserService.serialize(user)

    @staticmethod
    def reset_password(user_id: str, password: str):
        ctx = require_request_context()
        user = UserRepository.get_by_id_and_tenant(user_id, ctx.tenant_id)
        if user is None:
            raise NotFoundError("User not found")
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        user.password_hash = hash_password(password)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_USER",
            entity_type="USER",
            entity_id=user.id,
            new_data={"password_reset": True, "email": user.email},
        )
        db.session.commit()
        return {"message": "Password updated successfully"}

    @staticmethod
    def _validate_user_payload(name, email, password, require_password=False):
        if not name or not name.strip():
            raise ValidationError("Name is required")
        if not email or "@" not in email:
            raise ValidationError("A valid email is required")
        if require_password and (not password or len(password) < 8):
            raise ValidationError("Password must be at least 8 characters")

    @staticmethod
    def serialize(user: User):
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role_name,
            "is_active": user.is_active,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }