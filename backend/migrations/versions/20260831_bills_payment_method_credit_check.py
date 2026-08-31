"""Allow credit (udhari) in bills.payment_method CHECK constraint.

Some hosted databases were created with chk_bills_payment_method allowing only
cash/online. Credit sales then fail with HTTP 500 (MySQL constraint violation).

Revision ID: 20260831_bills_payment_method_credit_check
Revises: 20260827_cafe_coupons
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect, text

revision = "20260831_bills_payment_method_credit_check"
down_revision = "20260827_cafe_coupons"
branch_labels = None
depends_on = None

_PAYMENT_CHECK = "chk_bills_payment_method"
_PAYMENT_CLAUSE = "payment_method IN ('cash', 'online', 'credit')"


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _drop_payment_check(bind) -> None:
    for stmt in (
        f"ALTER TABLE bills DROP CONSTRAINT {_PAYMENT_CHECK}",
        f"ALTER TABLE bills DROP CHECK {_PAYMENT_CHECK}",
    ):
        try:
            bind.execute(text(stmt))
            return
        except Exception:
            continue


def upgrade() -> None:
    if not _has_table("bills"):
        return
    bind = op.get_bind()
    _drop_payment_check(bind)
    try:
        bind.execute(
            text(
                f"ALTER TABLE bills ADD CONSTRAINT {_PAYMENT_CHECK} "
                f"CHECK ({_PAYMENT_CLAUSE})"
            )
        )
    except Exception:
        # Constraint may already be correct or unsupported on this engine.
        pass


def downgrade() -> None:
    if not _has_table("bills"):
        return
    bind = op.get_bind()
    _drop_payment_check(bind)
    try:
        bind.execute(
            text(
                f"ALTER TABLE bills ADD CONSTRAINT {_PAYMENT_CHECK} "
                "CHECK (payment_method IN ('cash', 'online'))"
            )
        )
    except Exception:
        pass
