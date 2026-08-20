"""Idempotent CHECK constraint helpers for MySQL 8 and MariaDB."""

from __future__ import annotations

from sqlalchemy import text


def check_clause(conn, name: str) -> str | None:
    row = conn.execute(
        text(
            """
            SELECT CHECK_CLAUSE
            FROM information_schema.CHECK_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = DATABASE()
              AND CONSTRAINT_NAME = :name
            """
        ),
        {"name": name},
    ).fetchone()
    return row[0] if row else None


def drop_check_constraint(conn, table: str, name: str) -> bool:
    """Drop a CHECK constraint. MariaDB wants DROP CONSTRAINT; MySQL 8 accepts DROP CHECK."""
    if check_clause(conn, name) is None:
        return False
    statements = (
        f"ALTER TABLE `{table}` DROP CONSTRAINT `{name}`",
        f"ALTER TABLE `{table}` DROP CHECK `{name}`",
    )
    for stmt in statements:
        try:
            conn.execute(text("SAVEPOINT drop_chk"))
            conn.execute(text(stmt))
            conn.execute(text("RELEASE SAVEPOINT drop_chk"))
            return True
        except Exception:
            try:
                conn.execute(text("ROLLBACK TO SAVEPOINT drop_chk"))
            except Exception:
                pass
    return False
