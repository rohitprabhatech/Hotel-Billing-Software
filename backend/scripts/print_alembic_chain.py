"""Print the linear Alembic revision chain (BIZ-67 ops helper)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
VERSIONS = BACKEND_ROOT / "migrations" / "versions"


def load_revisions() -> list[tuple[str, str | None, str]]:
    rows: list[tuple[str, str | None, str]] = []
    for path in VERSIONS.glob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rev_m = re.search(r"^revision\s*=\s*[\"']([^\"']+)", text, re.M)
        down_m = re.search(r"^down_revision\s*=\s*(.+)$", text, re.M)
        if not rev_m:
            continue
        down = down_m.group(1).strip().rstrip(",") if down_m else "None"
        if down == "None":
            down_val: str | None = None
        else:
            down_val = down.strip("\"'")
        rows.append((rev_m.group(1), down_val, path.name))
    return rows


def chain_from_head(rows: list[tuple[str, str | None, str]]) -> tuple[str, list[tuple[str, str | None, str]]]:
    by = {rev: (rev, down, name) for rev, down, name in rows}
    children = {down for _, down, _ in rows if down}
    heads = [rev for rev, _, _ in rows if rev not in children]
    if len(heads) != 1:
        raise SystemExit(f"Expected exactly one Alembic head, found: {heads}")
    head = heads[0]
    lin: list[tuple[str, str | None, str]] = []
    cur: str | None = head
    while cur:
        lin.append(by[cur])
        cur = by[cur][1]
    lin.reverse()
    return head, lin


def main() -> int:
    rows = load_revisions()
    head, lin = chain_from_head(rows)
    print(f"HEAD\t{head}")
    for i, (rev, _down, name) in enumerate(lin, 1):
        print(f"{i:03d}\t{rev}\t{name}")
    print(f"TOTAL\t{len(lin)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
