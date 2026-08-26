"""Sprint BIZ-67 — migration chain integrity (repo dry-run)."""

import importlib.util
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "20260826_biz66_perf_indexes"
EXPECTED_COUNT = 56


def _load_chain_module():
    path = BACKEND / "scripts" / "print_alembic_chain.py"
    spec = importlib.util.spec_from_file_location("print_alembic_chain", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_alembic_chain_is_linear_single_head():
    mod = _load_chain_module()
    rows = mod.load_revisions()
    assert len(rows) == EXPECTED_COUNT
    head, lin = mod.chain_from_head(rows)
    assert head == EXPECTED_HEAD
    assert len(lin) == EXPECTED_COUNT
    ids = [rev for rev, _, _ in lin]
    assert len(ids) == len(set(ids))
    assert lin[0][1] is None
    for i in range(1, len(lin)):
        rev, down, _ = lin[i]
        assert down == lin[i - 1][0]


def test_ops_runbook_and_order_docs_exist():
    root = BACKEND.parent / "docs" / "03-database"
    runbook = root / "10-industry-modules-ops-runbook.md"
    order = root / "11-alembic-revision-order.md"
    assert runbook.is_file()
    assert order.is_file()
    text = runbook.read_text(encoding="utf-8")
    assert "02_schema.sql" in text
    assert EXPECTED_HEAD in text
    assert "business_type" in text
    assert EXPECTED_HEAD in order.read_text(encoding="utf-8")


def test_stamp_industry_script_points_at_head():
    script = BACKEND / "scripts" / "stamp_alembic_industry_head.py"
    text = script.read_text(encoding="utf-8")
    assert f'INDUSTRY_HEAD = "{EXPECTED_HEAD}"' in text
