"""Regenerate sql/02_schema.sql from SQLAlchemy metadata (MySQL greenfield only).

Never run the output against production data — it DROPs all tables first.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import CheckConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateIndex, CreateTable

from app import create_app
from app.extensions import db
import app.models  # noqa: F401
from app.models.item import Item
from app.models.role import Role


def _ensure_greenfield_checks() -> None:
    """Preserve historical CHECK constraints that models rely on at the DB layer."""
    if not any(
        isinstance(c, CheckConstraint) and "stock_quantity" in str(c.sqltext)
        for c in Item.__table__.constraints
    ):
        Item.__table__.append_constraint(
            CheckConstraint(
                "stock_quantity IS NULL OR stock_quantity >= 0",
                name="chk_items_stock",
            )
        )
    if not any(
        isinstance(c, CheckConstraint) and "OWNER" in str(c.sqltext)
        for c in Role.__table__.constraints
    ):
        Role.__table__.append_constraint(
            CheckConstraint(
                "name IN ('OWNER', 'BILLING_USER', 'MANAGER')",
                name="chk_roles_name",
            )
        )


def _topo_create_order(tables_map: dict) -> list[str]:
    remaining = set(tables_map)
    create_order: list[str] = []
    while remaining:
        progress = False
        for name in sorted(remaining):
            deps = {
                fk.column.table.name
                for fk in tables_map[name].foreign_keys
                if fk.column.table.name != name
            }
            if deps <= set(create_order):
                create_order.append(name)
                remaining.remove(name)
                progress = True
        if not progress:
            create_order.extend(sorted(remaining))
            break
    return create_order


def _fix_ddl(sql: str) -> str:
    sql = sql.replace("NUMERIC(", "DECIMAL(")
    sql = re.sub(r"\bBOOL\b", "TINYINT(1)", sql)
    sql = re.sub(r"\bBOOLEAN\b", "TINYINT(1)", sql)
    sql = re.sub(r"DEFAULT\s+now\(\)", "DEFAULT CURRENT_TIMESTAMP(6)", sql, flags=re.I)
    sql = re.sub(
        r"DEFAULT\s+CURRENT_TIMESTAMP(?!\()",
        "DEFAULT CURRENT_TIMESTAMP(6)",
        sql,
        flags=re.I,
    )
    return "\n".join(line.rstrip() for line in sql.splitlines())


def _with_engine(ddl: str) -> str:
    ddl = ddl.rstrip().rstrip(";")
    if "ENGINE=" in ddl:
        return ddl
    if ddl.endswith(")"):
        return ddl + " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    return ddl + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"


def _alembic_head() -> str:
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        cfg = Config()
        cfg.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
        script = ScriptDirectory.from_config(cfg)
        heads = list(script.get_heads())
        return heads[0] if len(heads) == 1 else ",".join(heads) or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def main() -> None:
    _ensure_greenfield_checks()
    app = create_app("testing")
    out_path = Path(__file__).resolve().parents[1] / "sql" / "02_schema.sql"
    alembic_head = _alembic_head()

    with app.app_context():
        dialect = mysql.dialect()
        tables_map = {t.name: t for t in db.metadata.tables.values()}
        create_order = _topo_create_order(tables_map)
        drop_order = list(reversed(create_order))

        lines: list[str] = [
            "-- =============================================================================",
            "-- Business Billing Software — MySQL Schema (Multi-Tenant)",
            "-- Database : hotel_billing  (legacy DB name; product is multi-business)",
            "-- Charset  : utf8mb4 / utf8mb4_unicode_ci",
            f"-- Tables   : {len(create_order)} application tables (aligned with SQLAlchemy models / Alembic)",
            f"-- Alembic head: {alembic_head}",
            "--",
            "-- GREENFIELD / EMPTY DB ONLY. DROP + recreate. Never run on production data.",
            "-- Upgrades: flask db upgrade  (preferred for existing / hosted DBs).",
            "-- Regenerated from SQLAlchemy metadata for cloud greenfield readiness.",
            "-- =============================================================================",
            "",
            "USE hotel_billing;",
            "",
            "SET NAMES utf8mb4;",
            "SET FOREIGN_KEY_CHECKS = 0;",
            "",
            "-- Drop (safe re-run for local/dev)",
        ]
        lines.extend(f"DROP TABLE IF EXISTS {name};" for name in drop_order)
        lines.extend(["", "SET FOREIGN_KEY_CHECKS = 0;", ""])

        for name in create_order:
            table = tables_map[name]
            lines.append(f"-- {name}")
            lines.append("")
            ddl = _with_engine(_fix_ddl(str(CreateTable(table).compile(dialect=dialect))))
            lines.append(ddl + ";")
            lines.append("")

            emitted: set[str] = set()
            for idx in table.indexes:
                key = idx.name or ",".join(idx.columns.keys())
                if key in emitted:
                    continue
                emitted.add(key)
                try:
                    idx_sql = _fix_ddl(str(CreateIndex(idx).compile(dialect=dialect)))
                    lines.append(idx_sql + ";")
                    lines.append("")
                except Exception as exc:  # noqa: BLE001
                    lines.append(f"-- skipped index {idx.name}: {exc}")
                    lines.append("")

        # Deferred FKs (use_alter=True) — emit after all CREATE TABLE statements
        alter_lines: list[str] = []
        for name in create_order:
            table = tables_map[name]
            for fk in table.foreign_key_constraints:
                if not getattr(fk, "use_alter", False):
                    continue
                cols = ", ".join(c.name for c in fk.columns)
                ref_table = list(fk.elements)[0].column.table.name
                ref_cols = ", ".join(e.column.name for e in fk.elements)
                ondelete = fk.ondelete or "RESTRICT"
                cname = fk.name or f"fk_{name}_{cols.replace(', ', '_')}"
                alter_lines.append(
                    f"ALTER TABLE {name} ADD CONSTRAINT {cname} "
                    f"FOREIGN KEY ({cols}) REFERENCES {ref_table} ({ref_cols}) "
                    f"ON DELETE {ondelete};"
                )
        if alter_lines:
            lines.append("-- Deferred foreign keys (cycle / use_alter)")
            lines.append("")
            lines.extend(alter_lines)
            lines.append("")

        # Roles / plans are seeded by app scripts (seed_demo_data / onboard), not here.
        # Historical greenfield schema also omitted role INSERTs.
        lines.extend(
            [
                "SET FOREIGN_KEY_CHECKS = 1;",
                "",
                "-- End greenfield schema.",
                "",
            ]
        )

        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        text = out_path.read_text(encoding="utf-8")
        created = set(re.findall(r"CREATE TABLE (\w+)", text))
        print(f"Wrote {out_path} with {len(create_order)} tables")
        print("missing models:", sorted(set(tables_map) - created))
        print("extra:", sorted(created - set(tables_map)))
        print("chk_items_stock:", "chk_items_stock" in text)


if __name__ == "__main__":
    main()
