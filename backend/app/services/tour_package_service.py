"""Tour package catalog + service billing path (BIZ-56).

Packages are not stock SKUs. Each package owns a linked Item with
stock_quantity=NULL so existing bills sell without stock deduction.
"""

from decimal import Decimal, InvalidOperation

from app.constants.permissions import PERM_BILLING, PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.extensions import db
from app.models.category import Category
from app.models.item import Item
from app.models.role import ROLE_BILLING_USER
from app.models.tour_package import TourPackage
from app.repositories.category_repository import CategoryRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.tour_package_repository import TourPackageRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "tour_packages"
PACKAGE_CATEGORY_NAME = "Tour Packages"


class TourPackageService:
    @staticmethod
    def _require(*, write: bool):
        require_permission(PERM_ITEMS_WRITE if write else PERM_ITEMS_READ)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can manage tour packages")
        return ctx, tenant

    @staticmethod
    def _parse_price(value, *, field="base_price") -> Decimal:
        try:
            amount = money(Decimal(str(value)))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError(f"{field} must be a valid amount") from exc
        if amount < 0:
            raise ValidationError(f"{field} cannot be negative")
        return amount

    @staticmethod
    def _parse_gst(value) -> Decimal:
        try:
            gst = money(Decimal(str(value if value is not None else 0)))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError("gst_percentage must be a valid number") from exc
        if gst < 0 or gst > 100:
            raise ValidationError("gst_percentage must be between 0 and 100")
        return gst

    @staticmethod
    def serialize(row: TourPackage) -> dict:
        item = row.item
        return {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "description": row.description,
            "destination": row.destination,
            "duration_days": row.duration_days,
            "base_price": float(row.base_price),
            "gst_percentage": float(row.gst_percentage),
            "item_id": row.item_id,
            "stock_tracked": bool(item and item.stock_quantity is not None),
            "is_active": bool(row.is_active),
            "notes": row.notes,
            "created_by": row.created_by,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def _ensure_package_category(tenant_id: str, created_by: str | None) -> Category:
        existing = (
            db.session.query(Category)
            .filter(
                Category.tenant_id == tenant_id,
                Category.name == PACKAGE_CATEGORY_NAME,
                Category.parent_id.is_(None),
            )
            .first()
        )
        if existing is not None:
            if not existing.is_active:
                existing.is_active = True
            return existing
        category = Category(
            id=new_uuid(),
            tenant_id=tenant_id,
            name=PACKAGE_CATEGORY_NAME,
            parent_id=None,
            is_active=True,
        )
        CategoryRepository.add(category)
        db.session.flush()
        return category

    @staticmethod
    def _sync_linked_item(package: TourPackage) -> None:
        item = ItemRepository.get_by_id_and_tenant(package.item_id, package.tenant_id)
        if item is None:
            raise ValidationError("Linked package item is missing")
        item.name = package.name
        item.description = package.description
        item.price = package.base_price
        item.gst_percentage = package.gst_percentage
        item.stock_quantity = None
        item.is_active = bool(package.is_active)
        item.sku = f"PKG-{package.code}"[:64]
        db.session.flush()

    @staticmethod
    def list_packages(*, q=None, active_only=False, page=1, per_page=50):
        ctx, _ = TourPackageService._require(write=False)
        rows, total = TourPackageRepository.list_for_tenant(
            ctx.tenant_id,
            q=q,
            active_only=bool(active_only),
            page=page,
            per_page=per_page,
        )
        return (
            [TourPackageService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_package(package_id: str):
        ctx, _ = TourPackageService._require(write=False)
        row = TourPackageRepository.get_by_id(ctx.tenant_id, package_id)
        if row is None:
            raise NotFoundError("Tour package not found")
        return TourPackageService.serialize(row)

    @staticmethod
    def create(
        *,
        code: str,
        name: str,
        base_price,
        description=None,
        destination=None,
        duration_days=None,
        gst_percentage=0,
        is_active=True,
        notes=None,
    ):
        ctx, _ = TourPackageService._require(write=True)
        code_value = (code or "").strip().upper()
        name_value = (name or "").strip()
        if not code_value or not name_value:
            raise ValidationError("code and name are required")
        if TourPackageRepository.get_by_code(ctx.tenant_id, code_value):
            raise ValidationError("Package code already exists")
        price = TourPackageService._parse_price(base_price)
        gst = TourPackageService._parse_gst(gst_percentage)

        category = TourPackageService._ensure_package_category(ctx.tenant_id, ctx.user_id)
        item = Item(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            category_id=category.id,
            created_by=ctx.user_id,
            name=name_value,
            sku=f"PKG-{code_value}"[:64],
            description=(description or "").strip() or None,
            price=price,
            gst_percentage=gst,
            stock_quantity=None,
            uom="pcs",
            is_active=bool(is_active),
        )
        ItemRepository.add(item)
        db.session.flush()

        package = TourPackage(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            code=code_value,
            name=name_value,
            description=(description or "").strip() or None,
            destination=(destination or "").strip() or None,
            duration_days=int(duration_days) if duration_days is not None else None,
            base_price=price,
            gst_percentage=gst,
            item_id=item.id,
            is_active=bool(is_active),
            notes=(notes or "").strip() or None,
            created_by=ctx.user_id,
        )
        TourPackageRepository.add(package)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_TOUR_PACKAGE",
            entity_type="TOUR_PACKAGE",
            entity_id=package.id,
            new_data={
                "code": code_value,
                "name": name_value,
                "base_price": float(price),
                "item_id": item.id,
            },
        )
        db.session.commit()
        return TourPackageService.serialize(package)

    @staticmethod
    def update(package_id: str, **fields):
        ctx, _ = TourPackageService._require(write=True)
        row = TourPackageRepository.get_by_id(ctx.tenant_id, package_id)
        if row is None:
            raise NotFoundError("Tour package not found")
        old = TourPackageService.serialize(row)

        if "code" in fields and fields["code"] is not None:
            code_value = (fields["code"] or "").strip().upper()
            if not code_value:
                raise ValidationError("code is required")
            existing = TourPackageRepository.get_by_code(ctx.tenant_id, code_value)
            if existing and existing.id != row.id:
                raise ValidationError("Package code already exists")
            row.code = code_value
        if "name" in fields and fields["name"] is not None:
            name_value = (fields["name"] or "").strip()
            if not name_value:
                raise ValidationError("name is required")
            row.name = name_value
        if "description" in fields:
            row.description = (fields["description"] or "").strip() or None
        if "destination" in fields:
            row.destination = (fields["destination"] or "").strip() or None
        if "duration_days" in fields:
            row.duration_days = (
                int(fields["duration_days"]) if fields["duration_days"] is not None else None
            )
        if "base_price" in fields and fields["base_price"] is not None:
            row.base_price = TourPackageService._parse_price(fields["base_price"])
        if "gst_percentage" in fields and fields["gst_percentage"] is not None:
            row.gst_percentage = TourPackageService._parse_gst(fields["gst_percentage"])
        if "is_active" in fields and fields["is_active"] is not None:
            row.is_active = bool(fields["is_active"])
        if "notes" in fields:
            row.notes = (fields["notes"] or "").strip() or None

        TourPackageService._sync_linked_item(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_TOUR_PACKAGE",
            entity_type="TOUR_PACKAGE",
            entity_id=row.id,
            old_data=old,
            new_data=TourPackageService.serialize(row),
        )
        db.session.commit()
        return TourPackageService.serialize(row)

    @staticmethod
    def bill_package(
        package_id: str,
        *,
        quantity=1,
        payment_method="cash",
        customer_id=None,
        customer_name=None,
        discount=0,
        reference=None,
    ):
        """Create a bill for the package via its untracked linked item."""
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)

        row = TourPackageRepository.get_by_id(ctx.tenant_id, package_id)
        if row is None or not row.is_active:
            raise NotFoundError("Tour package not found or inactive")
        item = ItemRepository.get_by_id_and_tenant(row.item_id, ctx.tenant_id)
        if item is None or item.stock_quantity is not None:
            raise ValidationError("Package linked item must be untracked (no stock)")

        from app.services.bill_service import BillService

        bill = BillService.create_bill(
            items=[{"item_id": row.item_id, "quantity": quantity}],
            discount=discount,
            reference=reference or row.code,
            payment_method=payment_method,
            customer_id=customer_id,
            customer_name=customer_name or None,
        )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="BILL_TOUR_PACKAGE",
            entity_type="TOUR_PACKAGE",
            entity_id=row.id,
            new_data={
                "bill_id": bill["id"] if isinstance(bill, dict) else bill.id,
                "quantity": float(quantity),
            },
        )
        db.session.commit()
        return {
            "package": TourPackageService.serialize(row),
            "bill": bill if isinstance(bill, dict) else BillService.serialize(bill),
        }
