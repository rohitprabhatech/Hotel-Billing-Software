"""Expense HTTP controller."""

from flask import request

from app.schemas.expense_schemas import create_expense_schema, update_expense_schema
from app.services.expense_service import ExpenseService
from app.utils.responses import success_response


def list_expenses():
    data, meta = ExpenseService.list_expenses(
        q=request.args.get("q"),
        category=request.args.get("category"),
        from_date=request.args.get("from"),
        to_date=request.args.get("to"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def expense_summary():
    return success_response(
        data=ExpenseService.expense_summary(
            category=request.args.get("category"),
            from_date=request.args.get("from"),
            to_date=request.args.get("to"),
        )
    )


def get_expense(expense_id: str):
    return success_response(data=ExpenseService.get_expense(expense_id))


def create_expense():
    payload = create_expense_schema.load(request.get_json() or {})
    data = ExpenseService.create_expense(
        category=payload.get("category"),
        amount=payload["amount"],
        expense_date=payload["expense_date"],
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)


def update_expense(expense_id: str):
    raw = request.get_json() or {}
    payload = update_expense_schema.load(raw)
    data = ExpenseService.update_expense(
        expense_id,
        category=payload.get("category") if "category" in raw else None,
        category_provided="category" in raw,
        amount=payload.get("amount") if "amount" in raw else None,
        amount_provided="amount" in raw,
        expense_date=payload.get("expense_date") if "expense_date" in raw else None,
        expense_date_provided="expense_date" in raw,
        notes=payload.get("notes") if "notes" in raw else None,
        notes_provided="notes" in raw,
    )
    return success_response(data=data)


def delete_expense(expense_id: str):
    data = ExpenseService.delete_expense(expense_id)
    return success_response(data=data)
