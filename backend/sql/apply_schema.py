"""Create hotel_billing database and apply schema (local helper)."""

from pathlib import Path
from urllib.parse import unquote, urlparse

import pymysql
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL missing in .env")

    parsed = urlparse(database_url)
    user = unquote(parsed.username or "")
    password = unquote(parsed.password or "")
    host = parsed.hostname or "localhost"
    port = parsed.port or 3306
    db_name = (parsed.path or "").lstrip("/") or "hotel_billing"

    sql_dir = Path(__file__).resolve().parent
    create_sql = (sql_dir / "01_create_database.sql").read_text(encoding="utf-8")
    schema_sql = (sql_dir / "02_schema.sql").read_text(encoding="utf-8")

    print(f"Connecting to MySQL at {host}:{port} as {user} ...")
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            for statement in _split_sql(create_sql):
                cur.execute(statement)
            print(f"Database ensured: {db_name}")

        conn.select_db(db_name)
        with conn.cursor() as cur:
            for statement in _split_sql(schema_sql):
                cur.execute(statement)
            cur.execute("SHOW TABLES")
            tables = [row[0] for row in cur.fetchall()]
            cur.execute("SELECT DATABASE()")
            current_db = cur.fetchone()[0]
            cur.execute("SELECT name FROM roles ORDER BY name")
            roles = [row[0] for row in cur.fetchall()]

        print(f"Connected database: {current_db}")
        print(f"Tables ({len(tables)}): {', '.join(tables)}")
        print(f"Seeded roles: {', '.join(roles)}")
        print("Schema applied successfully.")
    finally:
        conn.close()


def _split_sql(script: str):
    """Split SQL script into executable statements (simple ; splitter)."""
    statements = []
    buffer = []
    for line in script.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(buffer).strip()
            if stmt:
                statements.append(stmt)
            buffer = []
    if buffer:
        stmt = "\n".join(buffer).strip()
        if stmt:
            statements.append(stmt)
    return statements


if __name__ == "__main__":
    main()
