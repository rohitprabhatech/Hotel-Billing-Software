#!/usr/bin/env python3
"""Fix cross-links after docs restructure; fill remaining testing stubs."""
from pathlib import Path
import re

DOCS = Path(__file__).resolve().parent

REPLACEMENTS = [
    ("../../00-overview/requirements-traceability.md", "../../00-project-foundation/07-requirements-traceability.md"),
    ("../../00-overview/supported-business-types.md", "../../00-project-foundation/04-supported-business-types.md"),
    ("../../00-overview/product-overview.md", "../../00-project-foundation/01-project-overview.md"),
    ("../../00-overview/glossary.md", "../../00-project-foundation/06-glossary.md"),
    ("../../00-overview/terminology.md", "../../00-project-foundation/06-glossary.md"),
    ("../../06-database/business-specific-tables.md", "../../03-database/04-business-specific-tables.md"),
    ("../../06-database/common-tables.md", "../../03-database/03-common-tables.md"),
    ("../../06-database/database-overview.md", "../../03-database/01-database-overview.md"),
    ("../../06-database/relationships.md", "../../03-database/05-relationships.md"),
    ("../../06-database/migration-strategy.md", "../../03-database/09-migration-strategy.md"),
    ("../../12-sprints/sprint-overview.md", "../../14-sprints/sprint-tracker.md"),
    ("../../12-sprints/", "../../14-sprints/"),
    ("../../03-master-admin/", "../../06-master-admin/"),
    ("../../01-architecture/", "../../02-architecture/"),
    ("../../09-subscription/", "../../09-subscription/"),  # same
    ("../99-historical/README.md", "../archive/README.md"),
    ("../../99-historical/README.md", "../../archive/README.md"),
    ("./supported-business-types.md", "./04-supported-business-types.md"),
]

updated = 0
for path in DOCS.rglob("*.md"):
    if "archive" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    new = text
    for a, b in REPLACEMENTS:
        new = new.replace(a, b)
    if new != text:
        path.write_text(new, encoding="utf-8")
        updated += 1
        print(f"LINKFIX {path.relative_to(DOCS)}")

# Testing stubs 03, 04
stubs = {
    "10-testing/03-functional-testing.md": """# Functional Testing

Validate Common Core and industry packs against functional requirements.

- Billing create/pay/print
- Inventory receive/adjust/movements
- Tenant-scoped lists
- Master registration approval

See [01-testing-strategy.md](./01-testing-strategy.md) and [../12-testing-guides/](../12-testing-guides/).
""",
    "10-testing/04-api-testing.md": """# API Testing

- Auth token required
- Tenant header/context enforced
- Master Admin routes isolated
- Contract checks for billing, inventory, reports, master APIs

See [../07-api/01-api-overview.md](../07-api/01-api-overview.md).
""",
}

for rel, body in stubs.items():
    p = DOCS / rel
    if not p.exists():
        p.write_text(body, encoding="utf-8")
        print(f"STUB {rel}")

# Remove stray unnumbered leftovers in common (keep only ##-*.md and README)
for folder in [
    "04-common-modules",
    "06-master-admin",
    "07-api",
    "08-ui-ux",
    "09-subscription",
    "10-testing",
    "11-user-manual",
]:
    d = DOCS / folder
    if not d.exists():
        continue
    for p in d.glob("*.md"):
        if p.name.lower() == "readme.md":
            continue
        if not re.match(r"^\d{2}-", p.name):
            dest = DOCS / "archive" / "leftover-unnumbered" / folder
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / p.name
            if target.exists():
                target.unlink()
            p.rename(target)
            print(f"ARCHIVED leftover {folder}/{p.name}")

print(f"Updated files: {updated}")
