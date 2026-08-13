"""Category business logic."""

from app.extensions import db
from app.models.category import Category
from app.models.role import ROLE_BILLING_USER
from app.repositories.category_repository import CategoryRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_request_context


class CategoryService:
    @staticmethod
    def list_categories():
        ctx = require_request_context()
        active_only = ctx.role == ROLE_BILLING_USER
        categories = CategoryRepository.list_by_tenant(
            ctx.tenant_id, active_only=active_only
        )
        return [CategoryService.serialize(c) for c in categories]

    @staticmethod
    def get_category(category_id: str):
        ctx = require_request_context()
        category = CategoryRepository.get_by_id_and_tenant(category_id, ctx.tenant_id)
        if category is None:
            raise NotFoundError("Category not found")
        if ctx.role == ROLE_BILLING_USER and not category.is_active:
            raise NotFoundError("Category not found")
        return CategoryService.serialize(category)

    @staticmethod
    def _resolve_parent(tenant_id: str, parent_id: str | None) -> Category | None:
        if not parent_id:
            return None
        parent = CategoryRepository.get_by_id_and_tenant(parent_id, tenant_id)
        if parent is None:
            raise ValidationError("Parent category not found for this hotel")
        return parent

    @staticmethod
    def _assert_valid_parent(
        *,
        tenant_id: str,
        category_id: str | None,
        parent_id: str | None,
    ) -> Category | None:
        parent = CategoryService._resolve_parent(tenant_id, parent_id)
        if parent is None:
            return None
        if category_id and parent.id == category_id:
            raise ValidationError("Category cannot be its own parent")
        if category_id:
            descendants = CategoryRepository.list_descendant_ids(category_id, tenant_id)
            if parent.id in descendants:
                raise ValidationError(
                    "Cannot set a child category as parent (circular hierarchy)"
                )
        return parent

    @staticmethod
    def create_category(*, name: str, description: str | None, parent_id: str | None):
        ctx = require_request_context()
        name = (name or "").strip()
        if not name:
            raise ValidationError("Category name is required")

        parent = CategoryService._assert_valid_parent(
            tenant_id=ctx.tenant_id,
            category_id=None,
            parent_id=parent_id,
        )

        if CategoryRepository.find_by_tenant_parent_name(
            ctx.tenant_id, parent.id if parent else None, name
        ):
            raise ConflictError("Category with this name already exists")

        category = Category(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            parent_id=parent.id if parent else None,
            name=name,
            description=(description or "").strip() or None,
            is_active=True,
        )
        CategoryRepository.add(category)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_CATEGORY",
            entity_type="CATEGORY",
            entity_id=category.id,
            new_data=CategoryService.serialize(category),
        )
        db.session.commit()
        db.session.refresh(category)
        return CategoryService.serialize(category)

    @staticmethod
    def update_category(
        category_id: str,
        *,
        name: str | None,
        description: str | None,
        parent_id: str | None,
        parent_id_provided: bool,
    ):
        ctx = require_request_context()
        category = CategoryRepository.get_by_id_and_tenant(category_id, ctx.tenant_id)
        if category is None:
            raise NotFoundError("Category not found")

        old = CategoryService.serialize(category)

        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationError("Category name is required")
            category.name = name

        if description is not None:
            category.description = description.strip() or None

        if parent_id_provided:
            parent = CategoryService._assert_valid_parent(
                tenant_id=ctx.tenant_id,
                category_id=category.id,
                parent_id=parent_id,
            )
            category.parent_id = parent.id if parent else None

        existing = CategoryRepository.find_by_tenant_parent_name(
            ctx.tenant_id, category.parent_id, category.name
        )
        if existing and existing.id != category.id:
            raise ConflictError("Category with this name already exists")

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_CATEGORY",
            entity_type="CATEGORY",
            entity_id=category.id,
            old_data=old,
            new_data=CategoryService.serialize(category),
        )
        db.session.commit()
        db.session.refresh(category)
        return CategoryService.serialize(category)

    @staticmethod
    def set_status(category_id: str, is_active: bool):
        ctx = require_request_context()
        category = CategoryRepository.get_by_id_and_tenant(category_id, ctx.tenant_id)
        if category is None:
            raise NotFoundError("Category not found")

        if not is_active:
            child_count = CategoryRepository.count_children(category.id, ctx.tenant_id)
            if child_count > 0:
                raise ValidationError(
                    "Cannot deactivate a category that has child categories. "
                    "Reassign or deactivate the child categories first."
                )

        old = CategoryService.serialize(category)
        category.is_active = bool(is_active)
        action = "DEACTIVATE_CATEGORY" if not category.is_active else "UPDATE_CATEGORY"
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action=action,
            entity_type="CATEGORY",
            entity_id=category.id,
            old_data=old,
            new_data=CategoryService.serialize(category),
        )
        db.session.commit()
        return CategoryService.serialize(category)

    @staticmethod
    def serialize(category: Category):
        parent_name = None
        if category.parent_id:
            if getattr(category, "parent", None) is not None:
                parent_name = category.parent.name
            else:
                parent = CategoryRepository.get_by_id_and_tenant(
                    category.parent_id, category.tenant_id
                )
                parent_name = parent.name if parent else None

        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "parent_id": category.parent_id,
            "parent_category_id": category.parent_id,
            "parent_category_name": parent_name,
            "is_active": category.is_active,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None,
        }
