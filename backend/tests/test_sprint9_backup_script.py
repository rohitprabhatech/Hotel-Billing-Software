"""Sprint 9: MariaDB-safe helper SQL and backup script env guard."""

from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def test_plan_seed_does_not_cast_as_json():
    source = (BACKEND / "scripts" / "apply_subscription_plans.py").read_text(encoding="utf-8")
    assert "CAST(:features AS JSON)" not in source
    assert ":features)" in source


def test_check_drop_tries_constraint_then_check():
    source = (BACKEND / "scripts" / "schema_helpers.py").read_text(encoding="utf-8")
    assert "DROP CONSTRAINT" in source
    assert "DROP CHECK" in source
    assert "SAVEPOINT drop_chk" in source


def test_backup_script_is_read_only():
    source = (BACKEND / "scripts" / "backup_database.py").read_text(encoding="utf-8")
    assert "SHOW CREATE TABLE" in source
    assert "DROP TABLE" not in source.upper()
    assert "INSERT INTO" not in source
    assert "ALTER TABLE" not in source
