"""Supplier master business logic."""

from app.constants.permissions import PERM_SUPPLIERS_READ, PERM_SUPPLIERS_WRITE
from app.extensions import db
from app.models.supplier import Supplier
from app.repositories.supplier_repository import SupplierRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class SupplierService:
    @staticmethod
    def _normalize_gstin(value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        gstin = str(value).strip().upper()
        if len(gstin) > 15:
            raise ValidationError("GSTIN must be at most 15 characters")
        return gstin

    @staticmethod
    def _normalize_phone(
        *,
        phone_country_code: str | None,
        phone: str | None,
    ) -> tuple[str | None, str | None, str | None]:
        cc = (phone_country_code or "").strip() or None
        nat = (phone or "").strip() or None
        if not cc and not nat:
            return None, None, None
        from app.utils.phone import normalize_phone

        parsed = normalize_phone(country_code=cc, national_number=nat)
        return parsed["country_code"], parsed["national"], parsed["e164"]

    @staticmethod
    def _normalize_email(email: str | None) -> str | None:
        if email is None or not str(email).strip():
            return None
        from app.utils.email_address import normalize_email

        try:
            return normalize_email(email)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    @staticmethod
    def list_suppliers(*, q=None, is_active=None, page=1, per_page=50):
        require_permission(PERM_SUPPLIERS_READ)
        ctx = require_request_context()
        rows, total = SupplierRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            is_active=is_active,
            page=page,
            per_page=per_page,
        )
        return (
            [SupplierService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_supplier(supplier_id: str):
        require_permission(PERM_SUPPLIERS_READ)
        ctx = require_request_context()
        supplier = SupplierRepository.get_by_id_and_tenant(supplier_id, ctx.tenant_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")
        return SupplierService.serialize(supplier)

    @staticmethod
    def create_supplier(
        *,
        name: str,
        phone_country_code: str | None = None,
        phone: str | None = None,
        gstin: str | None = None,
        email: str | None = None,
        address: str | None = None,
        notes: str | None = None,
    ):
        require_permission(PERM_SUPPLIERS_WRITE)
        ctx = require_request_context()
        name = (name or "").strip()
        if not name:
            raise ValidationError("Supplier name is required")

        phone_cc, phone_nat, phone_e164 = SupplierService._normalize_phone(
            phone_country_code=phone_country_code,
            phone=phone,
        )
        gstin_store = SupplierService._normalize_gstin(gstin)
        email_store = SupplierService._normalize_email(email)

        if phone_e164:
            existing = SupplierRepository.find_by_phone_e164(ctx.tenant_id, phone_e164)
            if existing is not None:
                raise ConflictError("A supplier with this phone number already exists")
        if gstin_store:
            existing = SupplierRepository.find_by_gstin(ctx.tenant_id, gstin_store)
            if existing is not None:
                raise ConflictError("A supplier with this GSTIN already exists")

        supplier = Supplier(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            name=name,
            phone_country_code=phone_cc,
            phone_national=phone_nat,
            phone_e164=phone_e164,
            gstin=gstin_store,
            email=email_store,
            address=(address or "").strip() or None,
            notes=(notes or "").strip() or None,
            is_active=True,
        )
        SupplierRepository.add(supplier)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_SUPPLIER",
            entity_type="SUPPLIER",
            entity_id=supplier.id,
            new_data=SupplierService.serialize(supplier),
        )
        db.session.commit()
        return SupplierService.serialize(supplier)

    @staticmethod
    def update_supplier(
        supplier_id: str,
        *,
        name: str | None = None,
        phone_country_code: str | None = None,
        phone: str | None = None,
        phone_provided: bool = False,
        gstin: str | None = None,
        gstin_provided: bool = False,
        email: str | None = None,
        email_provided: bool = False,
        address: str | None = None,
        address_provided: bool = False,
        notes: str | None = None,
        notes_provided: bool = False,
    ):
        require_permission(PERM_SUPPLIERS_WRITE)
        ctx = require_request_context()
        supplier = SupplierRepository.get_by_id_and_tenant(supplier_id, ctx.tenant_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")

        old = SupplierService.serialize(supplier)

        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationError("Supplier name is required")
            supplier.name = name

        if phone_provided:
            phone_cc, phone_nat, phone_e164 = SupplierService._normalize_phone(
                phone_country_code=phone_country_code,
                phone=phone,
            )
            if phone_e164:
                existing = SupplierRepository.find_by_phone_e164(ctx.tenant_id, phone_e164)
                if existing is not None and existing.id != supplier.id:
                    raise ConflictError("A supplier with this phone number already exists")
            supplier.phone_country_code = phone_cc
            supplier.phone_national = phone_nat
            supplier.phone_e164 = phone_e164

        if gstin_provided:
            gstin_store = SupplierService._normalize_gstin(gstin)
            if gstin_store:
                existing = SupplierRepository.find_by_gstin(ctx.tenant_id, gstin_store)
                if existing is not None and existing.id != supplier.id:
                    raise ConflictError("A supplier with this GSTIN already exists")
            supplier.gstin = gstin_store

        if email_provided:
            supplier.email = SupplierService._normalize_email(email)

        if address_provided:
            supplier.address = (address or "").strip() or None

        if notes_provided:
            supplier.notes = (notes or "").strip() or None

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_SUPPLIER",
            entity_type="SUPPLIER",
            entity_id=supplier.id,
            old_data=old,
            new_data=SupplierService.serialize(supplier),
        )
        db.session.commit()
        return SupplierService.serialize(supplier)

    @staticmethod
    def deactivate_supplier(supplier_id: str):
        from app.utils.owner_access import require_owner

        require_owner()
        require_permission(PERM_SUPPLIERS_WRITE)
        ctx = require_request_context()
        supplier = SupplierRepository.get_by_id_and_tenant(supplier_id, ctx.tenant_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")

        old = SupplierService.serialize(supplier)
        if supplier.is_active:
            supplier.is_active = False
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="DEACTIVATE_SUPPLIER",
                entity_type="SUPPLIER",
                entity_id=supplier.id,
                old_data=old,
                new_data=SupplierService.serialize(supplier),
            )
            db.session.commit()
        return SupplierService.serialize(supplier)

    @staticmethod
    def set_status(supplier_id: str, is_active: bool):
        if not is_active:
            return SupplierService.deactivate_supplier(supplier_id)
        require_permission(PERM_SUPPLIERS_WRITE)
        ctx = require_request_context()
        supplier = SupplierRepository.get_by_id_and_tenant(supplier_id, ctx.tenant_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")
        old = SupplierService.serialize(supplier)
        supplier.is_active = True
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_SUPPLIER",
            entity_type="SUPPLIER",
            entity_id=supplier.id,
            old_data=old,
            new_data=SupplierService.serialize(supplier),
        )
        db.session.commit()
        return SupplierService.serialize(supplier)

    @staticmethod
    def serialize(supplier: Supplier):
        from app.utils.email_address import mask_email
        from app.utils.phone import mask_e164

        return {
            "id": supplier.id,
            "name": supplier.name,
            "phone_country_code": supplier.phone_country_code,
            "phone_national": supplier.phone_national,
            "phone_masked": mask_e164(supplier.phone_e164),
            "gstin": supplier.gstin,
            "email": supplier.email,
            "email_masked": mask_email(supplier.email),
            "address": supplier.address,
            "notes": supplier.notes,
            "balance": float(getattr(supplier, "balance", 0) or 0),
            "credit_limit": (
                float(supplier.credit_limit)
                if getattr(supplier, "credit_limit", None) is not None
                else None
            ),
            "is_active": supplier.is_active,
            "created_at": supplier.created_at.isoformat() if supplier.created_at else None,
            "updated_at": supplier.updated_at.isoformat() if supplier.updated_at else None,
        }
