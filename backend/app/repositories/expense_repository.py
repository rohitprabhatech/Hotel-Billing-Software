"""Expense data access — tenant scoped."""

from datetime import date

from sqlalchemy import func, or_

from app.extensions import db
from app.models.expense import Expense


class ExpenseRepository:
    @staticmethod
    def get_by_id_and_tenant(expense_id: str, tenant_id: str) -> Expense | None:
        return (
            db.session.query(Expense)
            .filter(Expense.id == expense_id, Expense.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        q: str | None = None,
        category: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Expense], int]:
        query = db.session.query(Expense).filter(Expense.tenant_id == tenant_id)
        if category:
            query = query.filter(Expense.category == category.strip())
        if from_date:
            query = query.filter(Expense.expense_date >= from_date)
        if to_date:
            query = query.filter(Expense.expense_date <= to_date)
        if q:
            term = q.strip()
            like = f"%{term}%"
            query = query.filter(
                or_(
                    Expense.category.ilike(like),
                    Expense.notes.ilike(like),
                )
            )
        total = query.with_entities(func.count(Expense.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(Expense.expense_date.desc(), Expense.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def summary_by_tenant(
        tenant_id: str,
        *,
        category: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> tuple[float, list[dict]]:
        query = db.session.query(Expense).filter(Expense.tenant_id == tenant_id)
        if category:
            query = query.filter(Expense.category == category.strip())
        if from_date:
            query = query.filter(Expense.expense_date >= from_date)
        if to_date:
            query = query.filter(Expense.expense_date <= to_date)

        grouped = (
            query.with_entities(
                Expense.category,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count"),
            )
            .group_by(Expense.category)
            .order_by(func.sum(Expense.amount).desc())
            .all()
        )
        breakdown = [
            {
                "category": row.category or "Uncategorized",
                "total": float(row.total or 0),
                "count": int(row.count or 0),
            }
            for row in grouped
        ]
        grand_total = sum(row["total"] for row in breakdown)
        return grand_total, breakdown

    @staticmethod
    def add(expense: Expense) -> Expense:
        db.session.add(expense)
        return expense

    @staticmethod
    def delete(expense: Expense) -> None:
        db.session.delete(expense)
