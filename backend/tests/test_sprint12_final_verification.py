"""Sprint 12: readiness checker reports Alembic version."""

from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_platform_ready.py"


def test_readiness_script_includes_alembic_and_phase8():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "alembic_version" in source
    assert "master_admins" in source
    assert "phase8_missing" in source
