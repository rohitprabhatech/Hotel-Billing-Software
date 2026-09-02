"""Customer master business logic."""

from decimal import Decimal, InvalidOperation

from app.constants.permissions import PERM_CUSTOMERS_READ, PERM_CUSTOMERS_WRITE
from app.extensions import db
from app.models.customer import Customer
from app.repositories.bill_repository import BillRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class CustomerService:
    @staticmethod
    def _parse_credit_limit(value) -> Decimal | None:
        if value is None or value == "":
            return None
        try:
            dec = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValidationError("Invalid credit limit") from exc
        if dec < 0:
            raise ValidationError("Credit limit cannot be negative")
        return dec

    @staticmethod
    def _normalize_contact(
        *,
        phone_country_code: str | None,
        phone: str | None,
        email: str | None,
    ) -> tuple[str | None, str | None, str | None, str | None]:
        phone_cc_store = None
        phone_national_store = None
        phone_e164 = None
        cc = (phone_country_code or "").strip() or None
        nat = (phone or "").strip() or None
        if cc or nat:
            from app.utils.phone import normalize_phone

            parsed = normalize_phone(country_code=cc, national_number=nat)
            phone_cc_store = parsed["country_code"]
            phone_national_store = parsed["national"]
            phone_e164 = parsed["e164"]

        email_store = None
        if email is not None and str(email).strip():
            from app.utils.email_address import normalize_email

            try:
                email_store = normalize_email(email)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc

        return phone_cc_store, phone_national_store, phone_e164, email_store

    @staticmethod
    def list_customers(*, q=None, is_active=None, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        ctx = require_request_context()
        rows, total = CustomerRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            is_active=is_active,
            page=page,
            per_page=per_page,
        )
        return (
            [CustomerService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_customer(customer_id: str):
        require_permission(PERM_CUSTOMERS_READ)
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")
        return CustomerService.serialize(customer)

    @staticmethod
    def create_customer(
        *,
        name: str,
        phone_country_code: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        credit_limit=None,
        notes: str | None = None,
    ):
        require_permission(PERM_CUSTOMERS_WRITE)
        ctx = require_request_context()
        name = (name or "").strip()
        if not name:
            raise ValidationError("Customer name is required")

        phone_cc, phone_nat, phone_e164, email_store = CustomerService._normalize_contact(
            phone_country_code=phone_country_code,
            phone=phone,
            email=email,
        )
        if phone_e164:
            existing = CustomerRepository.find_by_phone_e164(ctx.tenant_id, phone_e164)
            if existing is not None:
                raise ConflictError("A customer with this phone number already exists")

        customer = Customer(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            name=name,
            phone_country_code=phone_cc,
            phone_national=phone_nat,
            phone_e164=phone_e164,
            email=email_store,
            credit_limit=CustomerService._parse_credit_limit(credit_limit),
            notes=(notes or "").strip() or None,
            is_active=True,
        )
        CustomerRepository.add(customer)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_CUSTOMER",
            entity_type="CUSTOMER",
            entity_id=customer.id,
            new_data=CustomerService.serialize(customer),
        )
        db.session.commit()
        return CustomerService.serialize(customer)

    @staticmethod
    def update_customer(
        customer_id: str,
        *,
        name: str | None = None,
        phone_country_code: str | None = None,
        phone: str | None = None,
        phone_provided: bool = False,
        email: str | None = None,
        email_provided: bool = False,
        credit_limit=None,
        credit_limit_provided: bool = False,
        notes: str | None = None,
        notes_provided: bool = False,
    ):
        require_permission(PERM_CUSTOMERS_WRITE)
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")

        old = CustomerService.serialize(customer)

        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationError("Customer name is required")
            customer.name = name

        if phone_provided:
            phone_cc, phone_nat, phone_e164, _ = CustomerService._normalize_contact(
                phone_country_code=phone_country_code,
                phone=phone,
                email=None,
            )
            if phone_e164:
                existing = CustomerRepository.find_by_phone_e164(ctx.tenant_id, phone_e164)
                if existing is not None and existing.id != customer.id:
                    raise ConflictError("A customer with this phone number already exists")
            customer.phone_country_code = phone_cc
            customer.phone_national = phone_nat
            customer.phone_e164 = phone_e164

        if email_provided:
            _, _, _, email_store = CustomerService._normalize_contact(
                phone_country_code=None,
                phone=None,
                email=email,
            )
            customer.email = email_store

        if credit_limit_provided:
            customer.credit_limit = CustomerService._parse_credit_limit(credit_limit)

        if notes_provided:
            customer.notes = (notes or "").strip() or None

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_CUSTOMER",
            entity_type="CUSTOMER",
            entity_id=customer.id,
            old_data=old,
            new_data=CustomerService.serialize(customer),
        )
        db.session.commit()
        return CustomerService.serialize(customer)

    @staticmethod
    def deactivate_customer(customer_id: str):
        from app.utils.owner_access import require_owner

        require_owner()
        require_permission(PERM_CUSTOMERS_WRITE)
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")

        old = CustomerService.serialize(customer)
        if customer.is_active:
            customer.is_active = False
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="DEACTIVATE_CUSTOMER",
                entity_type="CUSTOMER",
                entity_id=customer.id,
                old_data=old,
                new_data=CustomerService.serialize(customer),
            )
            db.session.commit()
        return CustomerService.serialize(customer)

    @staticmethod
    def set_status(customer_id: str, is_active: bool):
        if not is_active:
            return CustomerService.deactivate_customer(customer_id)
        require_permission(PERM_CUSTOMERS_WRITE)
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")
        old = CustomerService.serialize(customer)
        customer.is_active = True
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_CUSTOMER",
            entity_type="CUSTOMER",
            entity_id=customer.id,
            old_data=old,
            new_data=CustomerService.serialize(customer),
        )
        db.session.commit()
        return CustomerService.serialize(customer)

    @staticmethod
    def list_customer_bills(customer_id: str, *, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")

        bills, total = BillRepository.list_by_tenant(
            ctx.tenant_id,
            customer_id=customer_id,
            page=page,
            per_page=per_page,
        )
        from app.services.bill_service import BillService

        return (
            [BillService.serialize(b) for b in bills],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def resolve_for_bill(customer_id: str | None):
        """Load an active customer for bill linking (no permission decorator — billing path)."""
        if not customer_id:
            return None
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None or not customer.is_active:
            raise ValidationError("Customer not found or inactive")
        return customer

    @staticmethod
    def serialize(customer: Customer):
        from app.utils.email_address import mask_email
        from app.utils.phone import mask_e164

        return {
            "id": customer.id,
            "name": customer.name,
            "phone_country_code": customer.phone_country_code,
            "phone_national": customer.phone_national,
            "phone_masked": mask_e164(customer.phone_e164),
            "email": customer.email,
            "email_masked": mask_email(customer.email),
            "credit_limit": float(customer.credit_limit) if customer.credit_limit is not None else None,
            "balance": float(customer.balance or 0),
            "notes": customer.notes,
            "is_active": customer.is_active,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
        }
