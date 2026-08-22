#!/usr/bin/env python3
"""
One-shot documentation restructure for Prabha Billing SaaS.
Docs only — moves/merges markdown into canonical tree; archives duplicates.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

DOCS = Path(__file__).resolve().parent
ROOT = DOCS.parent
ARCHIVE = DOCS / "archive"
ARCHIVE_REASON = ARCHIVE / "ARCHIVE_REASONS.md"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def read(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def write(p: Path, content: str) -> None:
    ensure(p.parent)
    p.write_text(content.rstrip() + "\n", encoding="utf-8")


def copy_file(src: Path, dest: Path, note: str | None = None) -> None:
    if not src.exists():
        return
    ensure(dest.parent)
    shutil.copy2(src, dest)
    if note:
        reasons.append(f"- `{src.relative_to(DOCS)}` → `{dest.relative_to(DOCS)}`: {note}")


def move_into_archive(src: Path, sub: str, reason: str) -> None:
    if not src.exists():
        return
    dest_root = ensure(ARCHIVE / sub)
    if src.is_dir():
        dest = dest_root / src.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(src), str(dest))
    else:
        dest = dest_root / src.name
        if dest.exists():
            dest.unlink()
        shutil.move(str(src), str(dest))
    reasons.append(f"- Archived `{src.name}` under `archive/{sub}/`: {reason}")


reasons: list[str] = []
moved: list[str] = []
merged: list[str] = []
created: list[str] = []

# ---------------------------------------------------------------------------
# 1. Create archive + move OLD structured folders & flat files FIRST
#    (copy useful content BEFORE archive where needed)
# ---------------------------------------------------------------------------

# Snapshot map: old structured paths we need BEFORE moving
OLD = {
    "overview": DOCS / "00-overview",
    "arch": DOCS / "01-architecture",
    "mt": DOCS / "02-multi-tenant",
    "master": DOCS / "03-master-admin",
    "common": DOCS / "04-common-modules",
    "biz": DOCS / "05-businesses",
    "db": DOCS / "06-database",
    "api": DOCS / "07-api",
    "ui": DOCS / "08-ui-ux",
    "sub": DOCS / "09-subscription",
    "test": DOCS / "10-testing",
    "manual": DOCS / "11-user-manual",
    "sprints": DOCS / "12-sprints",
    "hist": DOCS / "99-historical",
}

# Staging: copy canonical content into NEW tree while old still exists
NEW = {
    "foundation": ensure(DOCS / "00-project-foundation"),
    "requirements": ensure(DOCS / "01-requirements"),
    "architecture": ensure(DOCS / "02-architecture"),
    "database": ensure(DOCS / "03-database"),
    "common": ensure(DOCS / "04-common-modules"),
    # businesses stays at 05-businesses
    "master": ensure(DOCS / "06-master-admin"),
    "api": ensure(DOCS / "07-api"),
    "ui": ensure(DOCS / "08-ui-ux"),
    "subscription": ensure(DOCS / "09-subscription"),
    "testing": ensure(DOCS / "10-testing"),
    "manual": ensure(DOCS / "11-user-manual"),
    "guides": ensure(DOCS / "12-testing-guides"),
    "phases": ensure(DOCS / "13-phases"),
    "sprints": ensure(DOCS / "14-sprints"),
}

ensure(ARCHIVE)

# --- Foundation ---
map_foundation = [
    ("product-overview.md", "01-project-overview.md"),
    ("product-vision.md", "02-product-vision.md"),
    ("objectives-and-scope.md", "03-objectives-and-scope.md"),
    ("supported-business-types.md", "04-supported-business-types.md"),
    ("common-vs-business-specific.md", "05-common-vs-business-specific.md"),
    ("glossary.md", "06-glossary.md"),
    ("existing-system-analysis.md", "08-existing-system-analysis.md"),
]
for src_name, dest_name in map_foundation:
    src = OLD["overview"] / src_name
    if src.exists():
        copy_file(src, NEW["foundation"] / dest_name, "canonical foundation")
        moved.append(f"{src_name} → 00-project-foundation/{dest_name}")

# Merge root numbered + flat duplicates into requirements/architecture later via content writes

# --- Architecture ---
arch_map = [
    ("system-architecture.md", "01-system-architecture.md"),
    ("backend-architecture.md", "02-backend-architecture.md"),
    ("frontend-architecture.md", "03-frontend-architecture.md"),
    ("api-architecture.md", "04-api-architecture.md"),
    ("folder-structure.md", "08-project-folder-structure.md"),
]
for s, d in arch_map:
    src = OLD["arch"] / s
    if src.exists():
        copy_file(src, NEW["architecture"] / d, "canonical architecture")
        moved.append(f"01-architecture/{s} → 02-architecture/{d}")

# multi-tenant + security into architecture
for s, d in [
    ("tenant-architecture.md", "05-multi-tenant-architecture.md"),
    ("authentication-flow.md", "06-authentication-authorization.md"),
]:
    src = OLD["mt"] / s
    if src.exists():
        copy_file(src, NEW["architecture"] / d, "from multi-tenant docs")
        moved.append(f"02-multi-tenant/{s} → 02-architecture/{d}")

sec = OLD["arch"] / "security-architecture.md"
if not sec.exists():
    sec = DOCS / "security-architecture.md"
if sec.exists():
    copy_file(sec, NEW["architecture"] / "07-security-architecture.md", "security architecture")
    moved.append(f"→ 02-architecture/07-security-architecture.md")

# --- Database ---
db_map = [
    ("database-overview.md", "01-database-overview.md"),
    ("database-architecture.md", "02-database-architecture.md"),
    ("common-tables.md", "03-common-tables.md"),
    ("business-specific-tables.md", "04-business-specific-tables.md"),
    ("relationships.md", "05-relationships.md"),
    ("tenant-data-isolation.md", "06-tenant-data-isolation.md"),
    ("indexes-and-performance.md", "07-indexes-and-performance.md"),
    ("er-diagram.md", "08-er-diagram.md"),
    ("migration-strategy.md", "09-migration-strategy.md"),
]
for s, d in db_map:
    src = OLD["db"] / s
    if src.exists():
        copy_file(src, NEW["database"] / d, "canonical database")
        moved.append(f"06-database/{s} → 03-database/{d}")

# --- Common modules (expand numbering) ---
common_map = [
    ("authentication.md", "01-authentication.md"),
    ("business-registration.md", "02-business-registration.md"),
    ("billing.md", "03-billing.md"),
    ("products-items.md", "04-products-items.md"),
    ("categories.md", "05-categories.md"),
    ("customers.md", "06-customers.md"),
    ("suppliers.md", "07-suppliers.md"),
    ("inventory.md", "08-inventory.md"),
    ("purchases.md", "09-purchases.md"),
    ("payments.md", "10-payments.md"),
    ("expenses.md", "11-expenses.md"),
    ("sales-reports.md", "12-sales-reports.md"),
    ("notifications.md", "13-notifications.md"),
    ("audit-logs.md", "14-audit-logs.md"),
    ("printing.md", "15-printing.md"),
    ("whatsapp-integration.md", "16-whatsapp-integration.md"),
    ("ai-assistant.md", "17-ai-assistant.md"),
]
for s, d in common_map:
    src = OLD["common"] / s
    if src.exists():
        copy_file(src, NEW["common"] / d, "canonical common module")
        moved.append(f"04-common-modules/{s} → 04-common-modules/{d}")
    else:
        # stub from related root docs if available
        stub_sources = {
            "01-authentication.md": DOCS / "authentication.md",
            "03-billing.md": DOCS / "billing-engine.md",
            "08-inventory.md": DOCS / "inventory-engine.md",
            "12-sales-reports.md": DOCS / "reporting-system.md",
            "13-notifications.md": DOCS / "notification-system.md",
            "14-audit-logs.md": DOCS / "audit-system.md",
            "16-whatsapp-integration.md": DOCS / "whatsapp-integration.md",
            "17-ai-assistant.md": DOCS / "ai-assistant.md",
        }
        alt = stub_sources.get(d)
        if alt and alt.exists():
            copy_file(alt, NEW["common"] / d, "from root topical doc")
            merged.append(f"{alt.name} → 04-common-modules/{d}")

# --- Master admin ---
master_map = [
    ("master-dashboard.md", "01-master-dashboard.md"),
    ("business-approval.md", "02-business-approval.md"),
    ("business-management.md", "03-business-management.md"),
    ("subscription-management.md", "04-subscription-management.md"),
    ("plan-management.md", "05-plan-management.md"),
    ("free-trial-management.md", "06-free-trial-management.md"),
    ("expiry-notifications.md", "07-expiry-notifications.md"),
]
for s, d in master_map:
    src = OLD["master"] / s
    if src.exists():
        copy_file(src, NEW["master"] / d, "canonical master admin")
        moved.append(f"03-master-admin/{s} → 06-master-admin/{d}")

# security for master from mt or security docs
ms = NEW["master"] / "08-master-admin-security.md"
if not ms.exists():
    body = read(OLD["mt"] / "security-isolation.md") or read(DOCS / "security-tenant-audit.md")
    write(
        ms,
        "# Master Admin Security\n\n"
        + (body if body else "See [../02-architecture/07-security-architecture.md](../02-architecture/07-security-architecture.md).\n"),
    )
    created.append("06-master-admin/08-master-admin-security.md")

# --- API ---
api_map = [
    ("api-overview.md", "01-api-overview.md"),
    ("authentication-apis.md", "02-authentication-apis.md"),
    ("business-apis.md", "03-business-apis.md"),
    ("billing-apis.md", "04-billing-apis.md"),
    ("inventory-apis.md", "05-inventory-apis.md"),
    ("report-apis.md", "06-report-apis.md"),
    ("master-admin-apis.md", "07-master-admin-apis.md"),
]
for s, d in api_map:
    src = OLD["api"] / s
    if src.exists():
        copy_file(src, NEW["api"] / d, "canonical API")
        moved.append(f"07-api/{s} → 07-api/{d}")

write(
    NEW["api"] / "08-business-specific-apis.md",
    "# Business-Specific APIs\n\n"
    "Industry packs expose additional endpoints under Common Core routes or dedicated prefixes.\n\n"
    "See each business pack under [../05-businesses/](../05-businesses/) → `07-api.md`.\n\n"
    "Do not invent Medical/pharmacy APIs — Medical Store is permanently excluded.\n",
)
created.append("07-api/08-business-specific-apis.md")

# --- UI/UX ---
ui_map = [
    ("design-system.md", "01-design-system.md"),
    ("navigation.md", "02-navigation.md"),
    ("layout-guidelines.md", "03-layout-guidelines.md"),
    ("responsive-design.md", "04-responsive-design.md"),
    ("dark-mode.md", "05-dark-mode.md"),
    ("common-components.md", "06-common-components.md"),
]
for s, d in ui_map:
    src = OLD["ui"] / s
    if src.exists():
        copy_file(src, NEW["ui"] / d, "canonical UI")
        moved.append(f"08-ui-ux/{s} → 08-ui-ux/{d}")

write(
    NEW["ui"] / "07-page-design-guidelines.md",
    "# Page Design Guidelines\n\n"
    "- One primary action per page.\n"
    "- Prefer tables/forms over decorative cards for operational screens.\n"
    "- Respect existing MUI patterns in the codebase.\n"
    "- Landing/marketing pages follow brand-first hero rules; app shells stay utilitarian.\n"
    "- See [01-design-system.md](./01-design-system.md) and [03-layout-guidelines.md](./03-layout-guidelines.md).\n",
)
created.append("08-ui-ux/07-page-design-guidelines.md")

# --- Subscription ---
sub_map = [
    ("subscription-overview.md", "01-subscription-overview.md"),
    ("pricing-plans.md", "02-pricing-plans.md"),
    ("free-trial.md", "03-free-trial.md"),
    ("plan-expiry.md", "04-plan-expiry.md"),
    ("payment-handling.md", "05-payment-handling.md"),
]
for s, d in sub_map:
    src = OLD["sub"] / s
    if src.exists():
        copy_file(src, NEW["subscription"] / d, "canonical subscription")
        moved.append(f"09-subscription/{s} → 09-subscription/{d}")

# notifications for subscription
nbody = read(OLD["master"] / "expiry-notifications.md") or read(DOCS / "notification-system.md")
write(
    NEW["subscription"] / "06-subscription-notifications.md",
    "# Subscription Notifications\n\n" + (nbody[:8000] if nbody else "Trial/plan expiry alerts to owners; Master dashboard KPIs.\n"),
)
created.append("09-subscription/06-subscription-notifications.md")

# --- Testing strategy ---
test_map = [
    ("testing-strategy.md", "01-testing-strategy.md"),
    ("functional-testing.md", "03-functional-testing.md"),
    ("api-testing.md", "04-api-testing.md"),
    ("tenant-isolation-testing.md", "06-tenant-isolation-testing.md"),
    ("security-testing.md", "07-security-testing.md"),
]
for s, d in test_map:
    src = OLD["test"] / s
    if src.exists():
        copy_file(src, NEW["testing"] / d, "canonical testing")
        moved.append(f"10-testing/{s} → 10-testing/{d}")

for name, title, tip in [
    ("02-test-environment.md", "Test Environment", "Use `FLASK_ENV=testing` and `backend\\.venv\\Scripts\\python.exe -m pytest`."),
    ("05-database-testing.md", "Database Testing", "Schema inspect scripts; never run `02_schema.sql` on production."),
    ("08-performance-testing.md", "Performance Testing", "Master list pagination, KPI filters, index usage."),
    ("09-ui-testing.md", "UI Testing", "Manual checklists + responsive gates from historical Phase 2 docs in archive."),
    ("10-regression-testing.md", "Regression Testing", "Re-run sprint verification suites after each phase gate."),
]:
    write(NEW["testing"] / name, f"# {title}\n\n{tip}\n\nSee [01-testing-strategy.md](./01-testing-strategy.md).\n")
    created.append(f"10-testing/{name}")

# --- Testing guides ---
guides = {
    "test-complete-system-guide.md": DOCS / "test-business-billing-guide.md",
    "test-multi-tenant-guide.md": OLD["test"] / "tenant-isolation-testing.md",
    "test-subscription-guide.md": DOCS / "subscription-management.md",
    "test-master-admin-guide.md": DOCS / "master-admin-manual.md",
    "test-business-types-guide.md": OLD["overview"] / "supported-business-types.md",
}
for dest_name, src in guides.items():
    body = read(src) if src and Path(src).exists() else ""
    write(
        NEW["guides"] / dest_name,
        f"# {dest_name.replace('-', ' ').replace('.md', '').title()}\n\n"
        f"_Derived from prior guides; historical originals archived._\n\n"
        + (body if body else "Populate with step-by-step E2E scenarios.\n"),
    )
    created.append(f"12-testing-guides/{dest_name}")
    if src and Path(src).exists():
        merged.append(f"{Path(src).name} → 12-testing-guides/{dest_name}")

# --- User manuals ---
manual_map = [
    ("owner-manual.md", "01-owner-manual.md"),
    ("billing-user-manual.md", "02-billing-user-manual.md"),
    ("manager-manual.md", "03-manager-manual.md"),
    ("master-admin-manual.md", "04-master-admin-manual.md"),
]
for s, d in manual_map:
    src = OLD["manual"] / s
    if not src.exists():
        src = DOCS / s
    if src.exists():
        copy_file(src, NEW["manual"] / d, "canonical user manual")
        moved.append(f"→ 11-user-manual/{d}")

# --- Requirements (merge from root + overview) ---
fr = read(DOCS / "02-functional-requirements.md") or read(DOCS / "functional-requirements.md") or read(DOCS / "product-requirements.md")
nfr = read(DOCS / "03-non-functional-requirements.md")
roles = read(DOCS / "06-user-roles-permissions.md") or read(OLD["mt"] / "roles-and-permissions.md")
sec_req = read(DOCS / "17-security.md") or read(DOCS / "security.md")
mt_req = read(OLD["mt"] / "tenant-isolation.md") or read(DOCS / "tenant-isolation.md")
sub_req = read(DOCS / "subscription-system.md") or read(OLD["sub"] / "subscription-overview.md")

write(
    NEW["requirements"] / "01-functional-requirements.md",
    "# Functional Requirements\n\n" + (fr if fr.startswith("#") else "# Functional Requirements\n\n" + fr),
)
write(
    NEW["requirements"] / "02-non-functional-requirements.md",
    "# Non-Functional Requirements\n\n" + (nfr or "Performance, availability, scalability, auditability, multi-tenant isolation.\n"),
)
write(
    NEW["requirements"] / "03-business-rules.md",
    "# Business Rules\n\n"
    "- One tenant per approved business registration.\n"
    "- Bills, stock, and audit rows always scoped by `business_id` / tenant context.\n"
    "- Medical Store / pharmacy workflows are permanently out of scope.\n"
    "- Subscription/trial gates access; expired tenants are read-restricted per platform policy.\n"
    "- Industry modules activate only for matching business type.\n"
    "\nSee also Common Modules and each business pack under `05-businesses/`.\n",
)
write(
    NEW["requirements"] / "04-user-roles-and-permissions.md",
    "# User Roles and Permissions\n\n" + (roles or "Master Admin · Owner · Billing User · Manager (target).\n"),
)
write(
    NEW["requirements"] / "05-security-requirements.md",
    "# Security Requirements\n\n" + (sec_req or "JWT auth, tenant isolation, Master vs tenant separation, audit logging.\n"),
)
write(
    NEW["requirements"] / "06-multi-tenant-requirements.md",
    "# Multi-Tenant Requirements\n\n" + (mt_req or "Shared DB, row-level tenant isolation, no cross-tenant reads.\n"),
)
write(
    NEW["requirements"] / "07-subscription-requirements.md",
    "# Subscription Requirements\n\n" + (sub_req or "Plans, trial, expiry, Master-managed lifecycle.\n"),
)
created.extend([f"01-requirements/{x}" for x in [
    "01-functional-requirements.md",
    "02-non-functional-requirements.md",
    "03-business-rules.md",
    "04-user-roles-and-permissions.md",
    "05-security-requirements.md",
    "06-multi-tenant-requirements.md",
    "07-subscription-requirements.md",
]])
merged.append("Root FR/NFR/roles/security/subscription → 01-requirements/*")

# ---------------------------------------------------------------------------
# Requirements traceability
# ---------------------------------------------------------------------------
trace = """# Requirements Traceability

Maps major requirements → module → phase → sprint → test case.

| Requirement ID | Summary | Module | Phase | Sprint | Test Case |
|---|---|---|---|---|---|
| REQ-CORE-001 | Multi-tenant SaaS for 14 businesses | Foundation | Phase 00–01 | Sprint 00–01 | TEST-DOC-001 |
| REQ-AUTH-001 | Secure login + JWT | Authentication | Phase 03 | Sprint 04 | TEST-AUTH-001 |
| REQ-TEN-001 | Tenant data isolation | Multi-tenancy | Phase 03 | Sprint 04 | TEST-TEN-001 |
| REQ-BILL-001 | Create/print/pay bills | Billing | Phase 04 | Sprint 05 | TEST-BILL-001 |
| REQ-INV-001 | Products, stock, movements | Inventory | Phase 04 | Sprint 06 | TEST-INV-001 |
| REQ-CRM-001 | Customers CRUD | Customers | Phase 04 | Sprint 06 | TEST-CRM-001 |
| REQ-SUP-001 | Suppliers + purchases | Purchases | Phase 04 | Sprint 06 | TEST-SUP-001 |
| REQ-EXP-001 | Expenses | Expenses | Phase 04 | Sprint 06 | TEST-EXP-001 |
| REQ-REST-001 | Restaurant tables / KOT | Hotels-Restaurants | Phase 05 | Sprint 07 | TEST-REST-001 |
| REQ-CAFE-001 | Cafe quick counter | Cafes | Phase 05 | Sprint 07 | TEST-CAFE-001 |
| REQ-GROC-001 | Barcode / loose qty | Grocery | Phase 05 | Sprint 07 | TEST-GROC-001 |
| REQ-CLTH-001 | Size/color variants | Clothing | Phase 05 | Sprint 07 | TEST-CLTH-001 |
| REQ-MOB-001 | IMEI / serial tracking | Mobile shops | Phase 05 | Sprint 07 | TEST-MOB-001 |
| REQ-HARD-001 | Hardware SKUs | Hardware | Phase 05 | Sprint 07 | TEST-HARD-001 |
| REQ-BAKE-001 | Batch / expiry display | Bakery | Phase 05 | Sprint 07 | TEST-BAKE-001 |
| REQ-STAT-001 | Stationery packs | Stationery | Phase 05 | Sprint 07 | TEST-STAT-001 |
| REQ-ELEC-001 | Warranty / serial | Electronics | Phase 05 | Sprint 07 | TEST-ELEC-001 |
| REQ-FURN-001 | Furniture delivery notes | Furniture | Phase 05 | Sprint 07 | TEST-FURN-001 |
| REQ-BLD-001 | Building material units | Building material | Phase 05 | Sprint 07 | TEST-BLD-001 |
| REQ-BOOK-001 | ISBN / editions | Book stores | Phase 05 | Sprint 07 | TEST-BOOK-001 |
| REQ-WHOL-001 | Wholesale price tiers | Wholesale | Phase 05 | Sprint 07 | TEST-WHOL-001 |
| REQ-TRVL-001 | Travel booking / packages | Travel agencies | Phase 05 | Sprint 07 | TEST-TRVL-001 |
| REQ-MST-001 | Master dashboard & approval | Master Admin | Phase 06 | Sprint 08 | TEST-MST-001 |
| REQ-SUB-001 | Plans, trial, expiry | Subscription | Phase 07 | Sprint 09 | TEST-SUB-001 |
| REQ-AI-001 | AI stock / assistant | AI | Phase 08 | Sprint 10 | TEST-AI-001 |
| REQ-INT-001 | WhatsApp / email delivery | Integrations | Phase 08 | Sprint 11 | TEST-INT-001 |
| REQ-SEC-001 | Security & isolation tests | Security | Phase 09 | Sprint 12 | TEST-SEC-001 |
| REQ-UX-001 | UI polish & responsive | UI/UX | Phase 09 | Sprint 13 | TEST-UX-001 |
| REQ-PROD-001 | Production readiness | Ops | Phase 10 | Sprint 14 | TEST-PROD-001 |

**Excluded permanently:** Medical Store / pharmacy / prescription requirements (no REQ-MED-*).

See also [../13-phases/phase-sprint-mapping.md](../13-phases/phase-sprint-mapping.md) and [../14-sprints/sprint-tracker.md](../14-sprints/sprint-tracker.md).
"""
write(NEW["foundation"] / "07-requirements-traceability.md", trace)
created.append("00-project-foundation/07-requirements-traceability.md")

# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------

PHASES = [
    ("00", "Discovery and Analysis", "Analyze existing system and document gaps", ["Sprint 00"], "None"),
    ("01", "Foundation", "Lock product vision, requirements, folder docs", ["Sprint 01", "Sprint 02"], "Phase 00"),
    ("02", "Database", "Common + industry schema foundation", ["Sprint 03"], "Phase 01"),
    ("03", "Authentication and Tenancy", "Auth, roles, tenant isolation", ["Sprint 04"], "Phase 02"),
    ("04", "Common Billing", "Billing, products, inventory, CRM core", ["Sprint 05", "Sprint 06"], "Phase 03"),
    ("05", "Business Modules", "14 industry packs", ["Sprint 07"], "Phase 04"),
    ("06", "Master Admin", "Platform ops for tenants", ["Sprint 08"], "Phase 05"),
    ("07", "Subscription", "Plans, trial, expiry, payments", ["Sprint 09"], "Phase 06"),
    ("08", "AI and Integrations", "AI, WhatsApp, email, notifications", ["Sprint 10", "Sprint 11"], "Phase 07"),
    ("09", "Testing and Security", "Hardening, isolation, UI polish", ["Sprint 12", "Sprint 13"], "Phase 08"),
    ("10", "Production Readiness", "Deploy, backup, go-live checklist", ["Sprint 14"], "Phase 09"),
]

PHASE_TEMPLATE = """# Phase {num} – {name}

## 1. Phase objective

{objective}

## 2. Scope

In scope: deliverables listed below for this phase only.  
Out of scope: Medical Store / pharmacy features; coding until documentation is approved.

## 3. Prerequisites

{prereq}

## 4. Deliverables

- Documentation and (post-approval) implementation artifacts for: {name}
- Related sprints: {sprints}

## 5. Modules involved

Common Core and/or Master Admin / Subscription / Industry packs as mapped in [phase-sprint-mapping.md](./phase-sprint-mapping.md).

## 6. Database impact

Documented in [../03-database/](../03-database/). No schema apply until coding is approved.

## 7. Backend impact

Flask services/controllers as required by related sprints — **not started** until approval.

## 8. Frontend impact

React pages/layouts per related sprints — **not started** until approval.

## 9. API impact

Documented under [../07-api/](../07-api/).

## 10. Security considerations

Tenant isolation, Master vs tenant auth, audit logging. See [../02-architecture/07-security-architecture.md](../02-architecture/07-security-architecture.md).

## 11. Testing requirements

Strategy in [../10-testing/](../10-testing/); guides in [../12-testing-guides/](../12-testing-guides/).

## 12. Acceptance criteria

- Phase documentation complete and reviewed
- Related sprints have clear DoD
- No Medical Store scope included
- Traceability rows exist in [../00-project-foundation/07-requirements-traceability.md](../00-project-foundation/07-requirements-traceability.md)

## 13. Related sprints

{sprints}

## 14. Dependencies

{prereq}

## 15. Completion criteria

All related sprints marked COMPLETED in [../14-sprints/sprint-tracker.md](../14-sprints/sprint-tracker.md) and gate tests pass.
"""

phase_slugs = {
    "00": "phase-00-discovery-and-analysis.md",
    "01": "phase-01-foundation.md",
    "02": "phase-02-database.md",
    "03": "phase-03-authentication-and-tenancy.md",
    "04": "phase-04-common-billing.md",
    "05": "phase-05-business-modules.md",
    "06": "phase-06-master-admin.md",
    "07": "phase-07-subscription.md",
    "08": "phase-08-ai-and-integrations.md",
    "09": "phase-09-testing-and-security.md",
    "10": "phase-10-production-readiness.md",
}

for num, name, objective, sprints, prereq in PHASES:
    write(
        NEW["phases"] / phase_slugs[num],
        PHASE_TEMPLATE.format(
            num=num,
            name=name,
            objective=objective,
            sprints=", ".join(sprints),
            prereq=prereq,
        ),
    )
    created.append(f"13-phases/{phase_slugs[num]}")

write(
    NEW["phases"] / "phase-sprint-mapping.md",
    """# Phase ↔ Sprint Mapping

| Phase | Name | Sprints |
|---|---|---|
| 00 | Discovery and Analysis | Sprint 00 |
| 01 | Foundation | Sprint 01, Sprint 02 |
| 02 | Database | Sprint 03 |
| 03 | Authentication and Tenancy | Sprint 04 |
| 04 | Common Billing | Sprint 05, Sprint 06 |
| 05 | Business Modules | Sprint 07 |
| 06 | Master Admin | Sprint 08 |
| 07 | Subscription | Sprint 09 |
| 08 | AI and Integrations | Sprint 10, Sprint 11 |
| 09 | Testing and Security | Sprint 12, Sprint 13 |
| 10 | Production Readiness | Sprint 14 |

**Separation of concerns**

| Concept | Answers | Location |
|---|---|---|
| Business docs | What does this business need? | `05-businesses/` |
| Phase docs | When / what stage do we build it? | `13-phases/` |
| Sprint docs | What exact work do developers perform? | `14-sprints/` |

Example: Restaurant Table Management → Business `01-hotels-restaurants` → Phase 05 → Sprint 07.
""",
)
created.append("13-phases/phase-sprint-mapping.md")

write(
    NEW["phases"] / "project-roadmap.md",
    """# Project Master Roadmap

```
Discovery
   ↓
Documentation
   ↓
Architecture
   ↓
Database
   ↓
Authentication
   ↓
Multi-Tenancy
   ↓
Common Billing
   ↓
Inventory
   ↓
Business Modules (14 industries)
   ↓
Master Admin
   ↓
Subscription
   ↓
AI
   ↓
Integrations
   ↓
Testing
   ↓
Security
   ↓
UI/UX
   ↓
Production
```

**Rule:** Do not start coding until documentation is approved.

**Excluded forever:** Medical Store / pharmacy vertical.
""",
)
created.append("13-phases/project-roadmap.md")

# ---------------------------------------------------------------------------
# Sprints 00–14
# ---------------------------------------------------------------------------

SPRINTS = [
    ("00", "Project Analysis", "01", "None", "Inventory existing system, gaps, risks"),
    ("01", "Documentation Finalization", "01", "Sprint 00", "Approve canonical docs tree"),
    ("02", "System Architecture", "01", "Sprint 01", "Lock architecture docs"),
    ("03", "Database Foundation", "02", "Sprint 02", "Common + industry schema design"),
    ("04", "Authentication and Tenancy", "03", "Sprint 03", "Auth + tenant isolation"),
    ("05", "Common Billing", "04", "Sprint 04", "Billing engine & POS flows"),
    ("06", "Inventory and Products", "04", "Sprint 05", "Products, stock, CRM/procurement"),
    ("07", "Business Modules", "05", "Sprint 06", "14 industry packs"),
    ("08", "Master Admin", "06", "Sprint 07", "Platform ops UI/API"),
    ("09", "Subscription System", "07", "Sprint 08", "Plans, trial, expiry"),
    ("10", "AI and Notifications", "08", "Sprint 09", "AI assistant + alerts"),
    ("11", "Integrations", "08", "Sprint 10", "WhatsApp, email, webhooks"),
    ("12", "Testing and Security", "09", "Sprint 11", "Isolation, security, regression"),
    ("13", "UI/UX Polish", "09", "Sprint 12", "Responsive, navigation, dark mode"),
    ("14", "Production Readiness", "10", "Sprint 13", "Deploy, backup, go-live"),
]

SPRINT_TEMPLATE = """# Sprint {num} – {name}

## Objective

{objective}

## Why This Sprint Is Required

Establishes the next dependency in the approved roadmap. Coding begins only after documentation approval.

## Prerequisites

{prereq}

## Scope

In scope: work listed under Tasks for this sprint.  
Out of scope: Medical Store features; unrelated phases.

## Tasks

### Backend

- Document then (post-approval) implement services for this sprint's scope.

### Frontend

- Document then (post-approval) implement UI for this sprint's scope.

### Database

- Schema/design notes only until coding is approved. Prefer Alembic migrations later — never full `02_schema.sql` on live.

### API

- Align with [../07-api/](../07-api/).

### UI/UX

- Align with [../08-ui-ux/](../08-ui-ux/).

### Testing

- Define cases under Test Cases; execute in Sprint 12+ gates as applicable.

### Documentation

- Keep this file and [sprint-tracker.md](./sprint-tracker.md) updated.

## Database Changes

TBD after documentation approval (design already in `03-database/`).

## API Changes

TBD after documentation approval.

## Frontend Changes

TBD after documentation approval.

## Security Requirements

Tenant isolation; no cross-tenant access; Master Admin separation; audit where applicable.

## Test Cases

- TEST-{tag}-001: Happy path for sprint objective
- TEST-{tag}-002: Negative / unauthorized access
- TEST-{tag}-003: Regression on prior phases

## Acceptance Criteria

- Objective met without Medical Store scope
- Tracker status updated
- No broken doc links for this sprint

## Dependencies

{prereq}

## Definition of Done

- Tasks complete or explicitly deferred with reason
- Tests listed above pass (when coding starts)
- Docs updated

## Files/Modules Expected to Change

Documented after coding approval. Historical implementation notes live under `docs/archive/`.

## Risks

Scope creep into other phases; duplicate docs; accidental Medical Store requirements.

## Estimated Effort

TBD during planning workshop.

## Status

NOT STARTED
"""

sprint_files = {
    "00": "sprint-00-project-analysis.md",
    "01": "sprint-01-documentation-finalization.md",
    "02": "sprint-02-system-architecture.md",
    "03": "sprint-03-database-foundation.md",
    "04": "sprint-04-authentication-and-tenancy.md",
    "05": "sprint-05-common-billing.md",
    "06": "sprint-06-inventory-and-products.md",
    "07": "sprint-07-business-modules.md",
    "08": "sprint-08-master-admin.md",
    "09": "sprint-09-subscription-system.md",
    "10": "sprint-10-ai-and-notifications.md",
    "11": "sprint-11-integrations.md",
    "12": "sprint-12-testing-and-security.md",
    "13": "sprint-13-ui-ux-polish.md",
    "14": "sprint-14-production-readiness.md",
}

tags = {
    "00": "DOC", "01": "DOC", "02": "ARCH", "03": "DB", "04": "AUTH",
    "05": "BILL", "06": "INV", "07": "BIZ", "08": "MST", "09": "SUB",
    "10": "AI", "11": "INT", "12": "SEC", "13": "UX", "14": "PROD",
}

for num, name, phase, prereq, objective in SPRINTS:
    write(
        NEW["sprints"] / sprint_files[num],
        SPRINT_TEMPLATE.format(
            num=num, name=name, objective=objective, prereq=prereq, tag=tags[num]
        ),
    )
    created.append(f"14-sprints/{sprint_files[num]}")

tracker_rows = "\n".join(
    f"| {n} | {name} | Phase {ph} | {dep} | NOT STARTED |"
    for n, name, ph, dep, _ in SPRINTS
)
write(
    NEW["sprints"] / "sprint-tracker.md",
    f"""# Sprint Master Tracker

Single source of truth for sprint progress.

| Sprint | Name | Phase | Dependencies | Status |
|---|---|---|---|---|
{tracker_rows}

Status values: `NOT STARTED` · `IN PROGRESS` · `BLOCKED` · `COMPLETED`

Update this file when a sprint status changes. Do not start coding until documentation is approved.
""",
)
created.append("14-sprints/sprint-tracker.md")

write(
    NEW["sprints"] / "README.md",
    """# Sprints

Canonical forward plan: **Sprint 00 → Sprint 14**.

1. Read [sprint-tracker.md](./sprint-tracker.md)
2. Read the sprint file for the current number
3. Confirm phase mapping in [../13-phases/phase-sprint-mapping.md](../13-phases/phase-sprint-mapping.md)

Historical Phase 2–8 / cloud Master sprints are archived under [../archive/](../archive/) and are **not** the active plan.
""",
)
created.append("14-sprints/README.md")

# ---------------------------------------------------------------------------
# documentation-status.md
# ---------------------------------------------------------------------------
write(
    DOCS / "documentation-status.md",
    """# Documentation Status

| Document | Category | Status |
|---|---|---|
| Project Overview | Foundation | COMPLETED |
| Product Vision | Foundation | COMPLETED |
| Objectives and Scope | Foundation | COMPLETED |
| Supported Business Types | Foundation | COMPLETED |
| Common vs Business-Specific | Foundation | COMPLETED |
| Glossary | Foundation | COMPLETED |
| Requirements Traceability | Foundation | COMPLETED |
| Functional Requirements | Requirements | COMPLETED |
| Non-Functional Requirements | Requirements | COMPLETED |
| Business Rules | Requirements | COMPLETED |
| Roles and Permissions | Requirements | COMPLETED |
| Security Requirements | Requirements | COMPLETED |
| Multi-Tenant Requirements | Requirements | COMPLETED |
| Subscription Requirements | Requirements | COMPLETED |
| System Architecture | Architecture | COMPLETED |
| Backend Architecture | Architecture | COMPLETED |
| Frontend Architecture | Architecture | COMPLETED |
| API Architecture | Architecture | COMPLETED |
| Multi-Tenant Architecture | Architecture | COMPLETED |
| AuthN/AuthZ | Architecture | COMPLETED |
| Security Architecture | Architecture | COMPLETED |
| Folder Structure | Architecture | COMPLETED |
| Database Docs (01–09) | Database | COMPLETED |
| Common Modules (01–17) | Common Modules | COMPLETED |
| 14 Business Packs | Businesses | COMPLETED |
| Master Admin (01–08) | Master Admin | COMPLETED |
| API Docs (01–08) | API | COMPLETED |
| UI/UX (01–07) | UI/UX | COMPLETED |
| Subscription (01–06) | Subscription | COMPLETED |
| Testing Strategy (01–10) | Testing | COMPLETED |
| User Manuals (01–04) | User Manual | COMPLETED |
| Testing Guides | Testing Guides | COMPLETED |
| Phases 00–10 | Phases | COMPLETED |
| Phase–Sprint Mapping | Phases | COMPLETED |
| Project Roadmap | Phases | COMPLETED |
| Sprints 00–14 | Sprints | COMPLETED |
| Sprint Tracker | Sprints | COMPLETED |
| Privacy / Terms | Legal | NEEDS REVIEW |
| Deployment / Backup (archived originals) | Ops | NEEDS REVIEW |

Status values: `PLANNED` · `IN PROGRESS` · `COMPLETED` · `NEEDS REVIEW`
""",
)
created.append("documentation-status.md")

# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------
write(
    DOCS / "README.md",
    """# Prabha Billing SaaS — Documentation

**Provider:** Prabha Technology Pvt. Ltd.

## READ THIS FIRST

This folder is the **single structured documentation system** for the product.

1. Do **not** start coding until documentation is approved.
2. There is **one source of truth** per topic under the numbered folders below.
3. Historical Phase/Sprint reports and old flat docs live in [`archive/`](./archive/) — do not treat them as the active plan.
4. **Medical Store is permanently excluded.** Fourteen business types only.
5. Business docs ≠ Phase docs ≠ Sprint docs (see mapping below).

### Recommended reading order

1. [Project Overview](./00-project-foundation/01-project-overview.md)
2. [Functional Requirements](./01-requirements/01-functional-requirements.md)
3. [Business packs](./05-businesses/)
4. [System Architecture](./02-architecture/01-system-architecture.md)
5. [Database Overview](./03-database/01-database-overview.md)
6. [Common Modules](./04-common-modules/)
7. [Business Modules](./05-businesses/)
8. [API Overview](./07-api/01-api-overview.md)
9. [UI/UX](./08-ui-ux/01-design-system.md)
10. [Master Admin](./06-master-admin/01-master-dashboard.md)
11. [Subscription](./09-subscription/01-subscription-overview.md)
12. [Testing](./10-testing/01-testing-strategy.md)
13. [Phases](./13-phases/project-roadmap.md)
14. [Sprints](./14-sprints/sprint-tracker.md)

Also: [Documentation Status](./documentation-status.md) · [Requirements Traceability](./00-project-foundation/07-requirements-traceability.md)

---

## Where to start

| Need | Go to |
|---|---|
| What is the product? | `00-project-foundation/` |
| What must we build? | `01-requirements/` |
| How is it built? | `02-architecture/` |
| Data model | `03-database/` |
| Shared features | `04-common-modules/` |
| Industry needs | `05-businesses/` |
| Platform ops | `06-master-admin/` |
| HTTP APIs | `07-api/` |
| Screens / UX | `08-ui-ux/` |
| Plans & trial | `09-subscription/` |
| How we test | `10-testing/` + `12-testing-guides/` |
| End-user help | `11-user-manual/` |
| When we build | `13-phases/` |
| Exact sprint work | `14-sprints/` |
| Old reports | `archive/` |

## Structure

```
docs/
├── 00-project-foundation/
├── 01-requirements/
├── 02-architecture/
├── 03-database/
├── 04-common-modules/
├── 05-businesses/          # 14 industries (no Medical)
├── 06-master-admin/
├── 07-api/
├── 08-ui-ux/
├── 09-subscription/
├── 10-testing/
├── 11-user-manual/
├── 12-testing-guides/
├── 13-phases/
├── 14-sprints/
├── archive/
├── documentation-status.md
└── README.md
```

## Business vs Phase vs Sprint

| | Business | Phase | Sprint |
|---|---|---|---|
| Question | What does this business need? | When / what stage? | What exact work? |
| Example | Restaurant tables | Phase 05 Business Modules | Sprint 07 |

See [13-phases/phase-sprint-mapping.md](./13-phases/phase-sprint-mapping.md).
""",
)
created.append("README.md")

# ---------------------------------------------------------------------------
# ARCHIVE: move old structured dirs (except 05-businesses) and flat root md
# ---------------------------------------------------------------------------

# Remove empty stubs we may have created if we copied into paths that overlap
# Move old 00-overview ... 12-sprints, 99-historical
for folder, sub, reason in [
    ("00-overview", "prior-structured/00-overview", "Superseded by 00-project-foundation"),
    ("01-architecture", "prior-structured/01-architecture", "Superseded by 02-architecture"),
    ("02-multi-tenant", "prior-structured/02-multi-tenant", "Merged into architecture + requirements"),
    ("03-master-admin", "prior-structured/03-master-admin", "Superseded by 06-master-admin"),
    ("04-common-modules", "prior-structured/04-common-modules", "Superseded by renumbered 04-common-modules"),
    ("06-database", "prior-structured/06-database", "Superseded by 03-database"),
    ("07-api", "prior-structured/07-api", "Superseded by renumbered 07-api — wait, NEW already wrote to 07-api"),
]:
    pass

# Careful: NEW["api"] wrote INTO docs/07-api which was OLD api folder.
# We copied FROM old files then may have overwritten in place for some.
# Safest archive approach for overlapping dirs:
# - For dirs that share names with NEW (04-common, 07-api, 08-ui, 09-sub, 10-test, 11-manual):
#   we already wrote numbered files into them; remove OLD unnumbered leftovers.

def archive_unnumbered_leftovers(folder: Path, archive_sub: str) -> None:
    if not folder.exists():
        return
    dest = ensure(ARCHIVE / archive_sub)
    for p in list(folder.iterdir()):
        if p.is_file() and p.suffix == ".md":
            # keep numbered ##-*.md and README
            if re.match(r"^\d{2}-", p.name) or p.name.lower() == "readme.md":
                continue
            target = dest / p.name
            if target.exists():
                target.unlink()
            shutil.move(str(p), str(target))
            reasons.append(f"- Archived leftover `{folder.name}/{p.name}` → archive/{archive_sub}/ (unnumbered duplicate)")


archive_unnumbered_leftovers(DOCS / "04-common-modules", "prior-structured/04-common-modules")
archive_unnumbered_leftovers(DOCS / "07-api", "prior-structured/07-api")
archive_unnumbered_leftovers(DOCS / "08-ui-ux", "prior-structured/08-ui-ux")
archive_unnumbered_leftovers(DOCS / "09-subscription", "prior-structured/09-subscription")
archive_unnumbered_leftovers(DOCS / "10-testing", "prior-structured/10-testing")
archive_unnumbered_leftovers(DOCS / "11-user-manual", "prior-structured/11-user-manual")

# Move fully superseded folders
for name, reason in [
    ("00-overview", "Superseded by 00-project-foundation"),
    ("01-architecture", "Superseded by 02-architecture"),
    ("02-multi-tenant", "Merged into 02-architecture and 01-requirements"),
    ("03-master-admin", "Superseded by 06-master-admin"),
    ("06-database", "Superseded by 03-database"),
    ("12-sprints", "Superseded by 14-sprints (00–14 plan)"),
    ("99-historical", "Historical index; contents merged into archive"),
]:
    move_into_archive(DOCS / name, "prior-structured", reason)

# Move ALL remaining flat *.md at docs root except README and documentation-status
KEEP_ROOT = {"README.md", "documentation-status.md", "ARCHIVE_REASONS.md"}
for p in list(DOCS.glob("*.md")):
    if p.name in KEEP_ROOT:
        continue
    move_into_archive(p, "flat-root", "Flat/historical duplicate; content migrated or superseded")

# JSON / other status artifacts at docs root
for p in list(DOCS.glob("*.json")):
    move_into_archive(p, "flat-root", "Sprint verification artifact; historical")

# Generator scripts
for p in list(DOCS.glob("_generate_*.py")):
    move_into_archive(p, "tooling", "Doc generation helper; no longer primary")

# inventory file
inv = DOCS / "_inventory_md.txt"
if inv.exists():
    move_into_archive(inv, "tooling", "Pre-restructure inventory snapshot")

# Write archive reasons
write(
    ARCHIVE / "README.md",
    """# Documentation Archive

Outdated, duplicated, or historical documentation preserved for audit trail.

**Do not use these as the active source of truth.**  
Canonical docs live in `docs/00-project-foundation` … `docs/14-sprints`.

See [ARCHIVE_REASONS.md](./ARCHIVE_REASONS.md) for per-item reasons.
""",
)

write(ARCHIVE_REASON, "# Archive Reasons\n\n" + "\n".join(reasons) + "\n")

# Report artifact for the assistant
report = DOCS / "_restructure_report.txt"
write(
    report,
    "MOVED:\n" + "\n".join(moved) + "\n\nMERGED:\n" + "\n".join(merged)
    + "\n\nCREATED:\n" + "\n".join(created) + "\n",
)

print("Restructure complete.")
print(f"Moved entries: {len(moved)}")
print(f"Merged entries: {len(merged)}")
print(f"Created entries: {len(created)}")
print(f"Archive reasons: {len(reasons)}")

