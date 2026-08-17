"""Add global UNIQUE(users.email) — idempotent. App already enforces uniqueness."""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text


def _has_index(conn, table: str, index_name: str) -> bool:
    return bool(
        conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = :table
                  AND INDEX_NAME = :index_name
                """
            ),
            {"table": table, "index_name": index_name},
        ).scalar()
    )


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.begin() as conn:
        if _has_index(conn, "users", "uq_users_email"):
            print("uq_users_email already exists")
            return 0

        dupes = conn.execute(
            text(
                """
                SELECT email, COUNT(*) AS c
                FROM users
                GROUP BY email
                HAVING c > 1
                """
            )
        ).fetchall()
        if dupes:
            print("Cannot add uq_users_email — duplicate emails exist:", file=sys.stderr)
            for row in dupes:
                print(f"  {row[0]} x{row[1]}", file=sys.stderr)
            return 1

        conn.execute(text("ALTER TABLE users ADD UNIQUE KEY uq_users_email (email)"))
        print("Added uq_users_email")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
