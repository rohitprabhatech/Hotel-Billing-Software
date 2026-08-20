"""Sprint 11: Phase 8 Alembic revision is idempotent and does not drop tables."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "migrations" / "versions" / "20260818_phase8_saas.py"


def test_phase8_revision_chains_from_webhook_head():
    source = REV.read_text(encoding="utf-8")
    assert 'revision = "20260818_phase8_saas"' in source
    assert 'down_revision = "20260814_wa_webhook_status"' in source


def test_phase8_upgrade_does_not_drop_tables():
    source = REV.read_text(encoding="utf-8")
    upgrade = source.split("def downgrade")[0]
    assert "drop_table(" not in upgrade
    assert "DROP TABLE IF" not in upgrade.upper()
    assert not any(line.strip().upper().startswith("DROP TABLE") for line in upgrade.splitlines())


def test_phase8_downgrade_is_noop():
    source = REV.read_text(encoding="utf-8")
    downgrade = source.split("def downgrade")[-1]
    assert "DROP TABLE" not in downgrade.upper()
    assert "drop_table" not in downgrade
