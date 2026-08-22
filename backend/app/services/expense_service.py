"""Business expense tracking for P&L-style reporting."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.constants.permissions import PERM_EXPENSES_READ, PERM_EXPENSES_WRITE
from app.extensions import db
from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money
from app.utils.periods import local_now, parse_date
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class ExpenseService:
    @staticmethod
    def _tenant_tz() -> str:
        ctx = require_request_context()
        return getattr(ctx, "tenant_timezone", None) or "Asia/Kolkata"

    @staticmethod
    def _parse_amount(value) -> Decimal:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError("Invalid amount") from exc
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        return money(amount)

    @staticmethod
    def _parse_filter_date(value: str | None) -> date | None:
        if value is None or not str(value).strip():
            return None
        try:
            return parse_date(str(value).strip(), ExpenseService._tenant_tz()).date()
        except ValueError as exc:
            raise ValidationError("Dates must be YYYY-MM-DD") from exc

    @staticmethod
    def _normalize_category(value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        return str(value).strip()[:80]

    @staticmethod
    def list_expenses(
        *,
        q=None,
        category=None,
        from_date=None,
        to_date=None,
        page=1,
        per_page=50,
    ):
        require_permission(PERM_EXPENSES_READ)
        ctx = require_request_context()
        date_from = ExpenseService._parse_filter_date(from_date)
        date_to = ExpenseService._parse_filter_date(to_date)
        if date_from and date_to and date_from > date_to:
            raise ValidationError("from date cannot be after to date")

        rows, total = ExpenseRepository.list_by_tenant(
            ctx.tenant_id,
            q=q,
            category=category,
            from_date=date_from,
            to_date=date_to,
            page=page,
            per_page=per_page,
        )
        return (
            [ExpenseService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def expense_summary(*, category=None, from_date=None, to_date=None):
        require_permission(PERM_EXPENSES_READ)
        ctx = require_request_context()
        date_from = ExpenseService._parse_filter_date(from_date)
        date_to = ExpenseService._parse_filter_date(to_date)
        if date_from and date_to and date_from > date_to:
            raise ValidationError("from date cannot be after to date")

        total, breakdown = ExpenseRepository.summary_by_tenant(
            ctx.tenant_id,
            category=category,
            from_date=date_from,
            to_date=date_to,
        )
        return {
            "total": total,
            "from_date": date_from.isoformat() if date_from else None,
            "to_date": date_to.isoformat() if date_to else None,
            "by_category": breakdown,
        }

    @staticmethod
    def get_expense(expense_id: str):
        require_permission(PERM_EXPENSES_READ)
        ctx = require_request_context()
        expense = ExpenseRepository.get_by_id_and_tenant(expense_id, ctx.tenant_id)
        if expense is None:
            raise NotFoundError("Expense not found")
        return ExpenseService.serialize(expense)

    @staticmethod
    def create_expense(
        *,
        category: str | None,
        amount,
        expense_date: date | datetime | str,
        notes: str | None,
    ):
        require_permission(PERM_EXPENSES_WRITE)
        ctx = require_request_context()
        amount_value = ExpenseService._parse_amount(amount)
        category_value = ExpenseService._normalize_category(category)
        notes_value = (notes or "").strip() or None

        if isinstance(expense_date, str):
            expense_day = ExpenseService._parse_filter_date(expense_date)
        elif isinstance(expense_date, datetime):
            expense_day = expense_date.date()
        else:
            expense_day = expense_date
        if expense_day is None:
            raise ValidationError("expense_date is required")

        expense = Expense(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            category=category_value,
            amount=amount_value,
            expense_date=expense_day,
            notes=notes_value,
            created_by=ctx.user_id,
        )
        ExpenseRepository.add(expense)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_EXPENSE",
            entity_type="EXPENSE",
            entity_id=expense.id,
            new_data=ExpenseService.serialize(expense),
        )
        db.session.commit()
        db.session.refresh(expense)
        return ExpenseService.serialize(expense)

    @staticmethod
    def update_expense(
        expense_id: str,
        *,
        category=None,
        category_provided=False,
        amount=None,
        amount_provided=False,
        expense_date=None,
        expense_date_provided=False,
        notes=None,
        notes_provided=False,
    ):
        require_permission(PERM_EXPENSES_WRITE)
        ctx = require_request_context()
        expense = ExpenseRepository.get_by_id_and_tenant(expense_id, ctx.tenant_id)
        if expense is None:
            raise NotFoundError("Expense not found")

        old = ExpenseService.serialize(expense)
        if category_provided:
            expense.category = ExpenseService._normalize_category(category)
        if amount_provided:
            expense.amount = ExpenseService._parse_amount(amount)
        if expense_date_provided:
            if expense_date is None:
                raise ValidationError("expense_date cannot be null")
            if isinstance(expense_date, str):
                parsed = ExpenseService._parse_filter_date(expense_date)
            elif isinstance(expense_date, datetime):
                parsed = expense_date.date()
            else:
                parsed = expense_date
            expense.expense_date = parsed
        if notes_provided:
            expense.notes = (notes or "").strip() or None

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_EXPENSE",
            entity_type="EXPENSE",
            entity_id=expense.id,
            old_data=old,
            new_data=ExpenseService.serialize(expense),
        )
        db.session.commit()
        db.session.refresh(expense)
        return ExpenseService.serialize(expense)

    @staticmethod
    def delete_expense(expense_id: str):
        require_permission(PERM_EXPENSES_WRITE)
        ctx = require_request_context()
        expense = ExpenseRepository.get_by_id_and_tenant(expense_id, ctx.tenant_id)
        if expense is None:
            raise NotFoundError("Expense not found")

        old = ExpenseService.serialize(expense)
        ExpenseRepository.delete(expense)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_EXPENSE",
            entity_type="EXPENSE",
            entity_id=expense_id,
            old_data=old,
        )
        db.session.commit()
        return {"id": expense_id, "deleted": True}

    @staticmethod
    def default_expense_date() -> str:
        return local_now(ExpenseService._tenant_tz()).date().isoformat()

    @staticmethod
    def serialize(expense: Expense):
        return {
            "id": expense.id,
            "category": expense.category,
            "amount": float(expense.amount),
            "expense_date": expense.expense_date.isoformat(),
            "notes": expense.notes,
            "created_by": expense.created_by,
            "created_by_name": expense.creator.name if expense.creator else None,
            "created_at": expense.created_at.isoformat() if expense.created_at else None,
            "updated_at": expense.updated_at.isoformat() if expense.updated_at else None,
        }
