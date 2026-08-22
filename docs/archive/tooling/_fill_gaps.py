#!/usr/bin/env python3
"""Fill missing canonical docs from archive prior-structured + stubs."""
from pathlib import Path
import shutil

DOCS = Path(__file__).resolve().parent
A = DOCS / "archive" / "prior-structured"
FLAT = DOCS / "archive" / "flat-root"


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def copy_if_missing(src: Path, dest: Path) -> bool:
    if dest.exists() or not src.exists():
        return False
    ensure(dest.parent)
    shutil.copy2(src, dest)
    print(f"RESTORED {dest.relative_to(DOCS)} <- {src.relative_to(DOCS)}")
    return True


def write_if_missing(dest: Path, content: str) -> bool:
    if dest.exists():
        return False
    ensure(dest.parent)
    dest.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"STUB {dest.relative_to(DOCS)}")
    return True


# Foundation
pairs = [
    (A / "00-overview" / "product-overview.md", DOCS / "00-project-foundation" / "01-project-overview.md"),
    (A / "00-overview" / "product-vision.md", DOCS / "00-project-foundation" / "02-product-vision.md"),
    (A / "00-overview" / "supported-business-types.md", DOCS / "00-project-foundation" / "04-supported-business-types.md"),
    (A / "00-overview" / "common-vs-industry-features.md", DOCS / "00-project-foundation" / "05-common-vs-business-specific.md"),
    (A / "00-overview" / "terminology.md", DOCS / "00-project-foundation" / "06-glossary.md"),
    (FLAT / "existing-system-analysis.md", DOCS / "00-project-foundation" / "08-existing-system-analysis.md"),
]
for s, d in pairs:
    copy_if_missing(s, d)

write_if_missing(
    DOCS / "00-project-foundation" / "03-objectives-and-scope.md",
    """# Objectives and Scope

## Objectives

- Deliver one multi-tenant Prabha Billing SaaS for **14** business types.
- Extend Common Core (billing, inventory, customers, payments, reports) with industry packs.
- Preserve existing Master Admin, registration approval, plans/trial, WhatsApp/email, AI, and audit capabilities.

## In scope

- Documentation structure (this tree), then (after approval) implementation of Common Core gaps and 14 industry modules.
- Master Admin and subscription lifecycle (already largely implemented — extend, do not rebuild).

## Out of scope

- Medical Store / pharmacy / prescription workflows (permanent exclusion).
- Building 14 separate applications.
- Coding before documentation approval.

## Success criteria

- One source of truth per topic under `docs/`.
- Requirement → Phase → Sprint → Test traceability.
- Tenant isolation and Master vs tenant security maintained.
""",
)

# Architecture gaps
arch_pairs = [
    (A / "01-architecture" / "system-architecture.md", DOCS / "02-architecture" / "01-system-architecture.md"),
    (A / "01-architecture" / "backend-architecture.md", DOCS / "02-architecture" / "02-backend-architecture.md"),
    (A / "01-architecture" / "frontend-architecture.md", DOCS / "02-architecture" / "03-frontend-architecture.md"),
    (A / "01-architecture" / "api-architecture.md", DOCS / "02-architecture" / "04-api-architecture.md"),
    (A / "02-multi-tenant" / "tenant-architecture.md", DOCS / "02-architecture" / "05-multi-tenant-architecture.md"),
    (A / "02-multi-tenant" / "authentication.md", DOCS / "02-architecture" / "06-authentication-authorization.md"),
    (FLAT / "security-architecture.md", DOCS / "02-architecture" / "07-security-architecture.md"),
    (A / "01-architecture" / "project-structure.md", DOCS / "02-architecture" / "08-project-folder-structure.md"),
]
for s, d in arch_pairs:
    copy_if_missing(s, d)

# If 06 auth thin, append authorization
auth_dest = DOCS / "02-architecture" / "06-authentication-authorization.md"
auth_src2 = A / "02-multi-tenant" / "authorization.md"
if auth_dest.exists() and auth_src2.exists():
    body = auth_dest.read_text(encoding="utf-8", errors="replace")
    extra = auth_src2.read_text(encoding="utf-8", errors="replace")
    if "authorization" not in body.lower() or len(body) < 200:
        auth_dest.write_text(body.rstrip() + "\n\n---\n\n" + extra + "\n", encoding="utf-8")
        print("MERGED authorization into 06-authentication-authorization.md")

if not (DOCS / "02-architecture" / "07-security-architecture.md").exists():
    copy_if_missing(A / "02-multi-tenant" / "security.md", DOCS / "02-architecture" / "07-security-architecture.md")

# Database
db_pairs = [
    (A / "06-database" / "database-overview.md", DOCS / "03-database" / "01-database-overview.md"),
    (A / "06-database" / "database-architecture.md", DOCS / "03-database" / "02-database-architecture.md"),
    (A / "06-database" / "common-tables.md", DOCS / "03-database" / "03-common-tables.md"),
    (A / "06-database" / "business-specific-tables.md", DOCS / "03-database" / "04-business-specific-tables.md"),
    (A / "06-database" / "relationships.md", DOCS / "03-database" / "05-relationships.md"),
    (A / "06-database" / "tenant-data-model.md", DOCS / "03-database" / "06-tenant-data-isolation.md"),
    (A / "06-database" / "indexes.md", DOCS / "03-database" / "07-indexes-and-performance.md"),
    (A / "06-database" / "er-diagrams.md", DOCS / "03-database" / "08-er-diagram.md"),
    (A / "06-database" / "migration-strategy.md", DOCS / "03-database" / "09-migration-strategy.md"),
]
for s, d in db_pairs:
    copy_if_missing(s, d)

# Common modules
common_pairs = [
    (A / "04-common-modules" / "billing.md", DOCS / "04-common-modules" / "03-billing.md"),
    (A / "04-common-modules" / "products.md", DOCS / "04-common-modules" / "04-products-items.md"),
    (A / "04-common-modules" / "categories.md", DOCS / "04-common-modules" / "05-categories.md"),
    (A / "04-common-modules" / "customers.md", DOCS / "04-common-modules" / "06-customers.md"),
    (A / "04-common-modules" / "suppliers.md", DOCS / "04-common-modules" / "07-suppliers.md"),
    (A / "04-common-modules" / "inventory.md", DOCS / "04-common-modules" / "08-inventory.md"),
    (A / "04-common-modules" / "purchases.md", DOCS / "04-common-modules" / "09-purchases.md"),
    (A / "04-common-modules" / "payments.md", DOCS / "04-common-modules" / "10-payments.md"),
    (A / "04-common-modules" / "expenses.md", DOCS / "04-common-modules" / "11-expenses.md"),
    (A / "04-common-modules" / "reports.md", DOCS / "04-common-modules" / "12-sales-reports.md"),
    (A / "04-common-modules" / "notifications.md", DOCS / "04-common-modules" / "13-notifications.md"),
    (A / "04-common-modules" / "audit-logs.md", DOCS / "04-common-modules" / "14-audit-logs.md"),
    (A / "04-common-modules" / "printing.md", DOCS / "04-common-modules" / "15-printing.md"),
    (A / "04-common-modules" / "whatsapp-integration.md", DOCS / "04-common-modules" / "16-whatsapp-integration.md"),
    (A / "04-common-modules" / "ai-assistant.md", DOCS / "04-common-modules" / "17-ai-assistant.md"),
]
for s, d in common_pairs:
    copy_if_missing(s, d)

# Auth + registration for common
copy_if_missing(A / "02-multi-tenant" / "authentication.md", DOCS / "04-common-modules" / "01-authentication.md")
write_if_missing(
    DOCS / "04-common-modules" / "02-business-registration.md",
    """# Business Registration

Public registration request → Master Admin approval → tenant bootstrap (owner user, trial/plan).

Canonical detail also in:

- [../06-master-admin/02-business-approval.md](../06-master-admin/02-business-approval.md)
- Archived: `archive/flat-root/registration-approval-flow.md`

Status: largely implemented in baseline SaaS; V2 documents and extends industry-type selection at registration.
""",
)

# Master admin
master_pairs = [
    (A / "03-master-admin" / "master-dashboard.md", DOCS / "06-master-admin" / "01-master-dashboard.md"),
    (A / "03-master-admin" / "business-approval.md", DOCS / "06-master-admin" / "02-business-approval.md"),
    (A / "03-master-admin" / "business-management.md", DOCS / "06-master-admin" / "03-business-management.md"),
    (A / "03-master-admin" / "subscription-management.md", DOCS / "06-master-admin" / "04-subscription-management.md"),
    (A / "03-master-admin" / "plan-management.md", DOCS / "06-master-admin" / "05-plan-management.md"),
    (A / "03-master-admin" / "trial-management.md", DOCS / "06-master-admin" / "06-free-trial-management.md"),
    (A / "09-subscription" / "expiry-notifications.md", DOCS / "06-master-admin" / "07-expiry-notifications.md"),
]
for s, d in master_pairs:
    copy_if_missing(s, d)

write_if_missing(
    DOCS / "06-master-admin" / "08-master-admin-security.md",
    """# Master Admin Security

- Separate Master Admin authentication from tenant users.
- Never invent or commit Master passwords; seed only via controlled script + `.env`.
- Platform audit log for lifecycle actions.
- See [../02-architecture/07-security-architecture.md](../02-architecture/07-security-architecture.md).
""",
)

# API
api_pairs = [
    (A / "07-api" / "common-apis.md", DOCS / "07-api" / "01-api-overview.md"),
    (A / "07-api" / "authentication-apis.md", DOCS / "07-api" / "02-authentication-apis.md"),
    (A / "07-api" / "business-apis.md", DOCS / "07-api" / "03-business-apis.md"),
    (A / "07-api" / "billing-apis.md", DOCS / "07-api" / "04-billing-apis.md"),
    (A / "07-api" / "inventory-apis.md", DOCS / "07-api" / "05-inventory-apis.md"),
    (A / "07-api" / "report-apis.md", DOCS / "07-api" / "06-report-apis.md"),
    (A / "07-api" / "master-admin-apis.md", DOCS / "07-api" / "07-master-admin-apis.md"),
]
for s, d in api_pairs:
    copy_if_missing(s, d)

write_if_missing(
    DOCS / "07-api" / "08-business-specific-apis.md",
    """# Business-Specific APIs

Industry endpoints are documented per pack under `05-businesses/*/07-api.md`.

No Medical/pharmacy APIs.
""",
)

# Subscription
sub_pairs = [
    (A / "09-subscription" / "subscription-overview.md", DOCS / "09-subscription" / "01-subscription-overview.md"),
    (A / "09-subscription" / "plans.md", DOCS / "09-subscription" / "02-pricing-plans.md"),
    (A / "09-subscription" / "free-trial.md", DOCS / "09-subscription" / "03-free-trial.md"),
    (A / "09-subscription" / "expiry-notifications.md", DOCS / "09-subscription" / "04-plan-expiry.md"),
    (A / "09-subscription" / "billing-for-subscription.md", DOCS / "09-subscription" / "05-payment-handling.md"),
    (A / "09-subscription" / "expiry-notifications.md", DOCS / "09-subscription" / "06-subscription-notifications.md"),
]
for s, d in sub_pairs:
    copy_if_missing(s, d)

# Testing fill
test_pairs = [
    (A / "10-testing" / "testing-strategy.md", DOCS / "10-testing" / "01-testing-strategy.md"),
    (A / "10-testing" / "tenant-isolation-testing.md", DOCS / "10-testing" / "06-tenant-isolation-testing.md"),
    (A / "10-testing" / "security-testing.md", DOCS / "10-testing" / "07-security-testing.md"),
    (A / "10-testing" / "performance-testing.md", DOCS / "10-testing" / "08-performance-testing.md"),
    (A / "10-testing" / "regression-testing.md", DOCS / "10-testing" / "10-regression-testing.md"),
]
for s, d in test_pairs:
    copy_if_missing(s, d)

# Businesses README if missing
biz_readme = DOCS / "05-businesses" / "README.md"
write_if_missing(
    biz_readme,
    """# Business Documentation (14 industries)

Each folder answers: **What does this business need?**

Medical Store is **not** included.

| # | Folder |
|---|---|
| 01 | hotels-restaurants |
| 02 | cafes-tea-shops |
| 03 | grocery-kirana |
| 04 | clothing |
| 05 | mobile-shops |
| 06 | hardware |
| 07 | bakery-sweet-shops |
| 08 | stationery |
| 09 | electronics |
| 10 | furniture |
| 11 | building-material |
| 12 | book-stores |
| 13 | wholesale |
| 14 | travel-agencies |

Phase/Sprint mapping: industry work is primarily **Phase 05 / Sprint 07**.
""",
)

# Fix overview links that pointed to 99-historical
ov = DOCS / "00-project-foundation" / "01-project-overview.md"
if ov.exists():
    t = ov.read_text(encoding="utf-8", errors="replace")
    t2 = t.replace("../99-historical/README.md", "../archive/README.md")
    t2 = t2.replace("./supported-business-types.md", "./04-supported-business-types.md")
    if t2 != t:
        ov.write_text(t2, encoding="utf-8")
        print("UPDATED links in 01-project-overview.md")

print("Fill-gaps done.")
