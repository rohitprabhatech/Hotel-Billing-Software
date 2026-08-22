# -*- coding: utf-8 -*-
"""Generate remaining shared documentation sections."""
from pathlib import Path

DOCS = Path(__file__).resolve().parent


def w(rel: str, text: str) -> None:
    p = DOCS / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + "\n", encoding="utf-8")
    print("wrote", rel)


# --- 00 overview ---
w(
    "00-overview/common-vs-industry-features.md",
    """
# Common vs Industry Features

## What is common across all businesses?

| Area | Examples |
|------|----------|
| Platform | Auth, tenant, Master Admin, registration, subscription, trial |
| Commerce | Billing engine, payments, invoices, print/PDF, WhatsApp send |
| Catalog | Categories, products/services (shape varies) |
| Parties | Customers (and suppliers where enabled) |
| Ops | Notifications, audit, settings, reports shell, AI (optional) |
| Inventory kernel | Quantity modes, movements, low-stock (when product-based) |

## What changes by business type?

| Industry | Examples of what changes |
|----------|--------------------------|
| Restaurant | Tables, KOT, kitchen, recipes, wastage |
| Cafe | Add-ons, combos, optional KOT |
| Grocery | Barcode, units, credit/udhari, expiry |
| Clothing | Size, color, brand, variants, exchange |
| Mobile | IMEI, warranty, repair |
| Hardware | UOM, bulk, price history, credit |
| Bakery | Batches, cake orders, production wastage |
| Stationery | Fast search POS, brands, bulk price |
| Electronics | Serial, warranty, install, repair |
| Furniture | Specs, quotes, custom orders, delivery |
| Building material | Warehouses, challans, transport, measure |
| Books | ISBN metadata, returns |
| Wholesale | Price lists, PO/SO, warehouses, outstanding |
| Travel | Packages, bookings, itinerary, commission (service-first) |

## Configuration idea (pre-implementation)

```
BusinessType → enabled Modules/Features → Navigation + API allow-list + Dashboard widgets
```

Restaurant: Billing=YES, Tables=YES, KOT=YES, IMEI=NO, Travel Booking=NO  
Clothing: Billing=YES, Size/Color=YES, KOT=NO  
Travel: Billing=YES (service), Inventory=LIGHT/NO, Packages=YES

See [business-feature-matrix.md](./business-feature-matrix.md).
""",
)

w(
    "00-overview/terminology.md",
    """
# Terminology

| Term | Meaning |
|------|---------|
| Tenant | One registered business workspace |
| Master Admin | Prabha Technology platform operator |
| Common Core | Shared modules used by many industries |
| Industry Pack | Business-specific modules/features |
| Bill / Invoice | Sale document from common billing engine |
| Product line | Stockable catalog line |
| Service line | Non-stock / package / fee line |
| KOT | Kitchen Order Ticket (F&B) |
| Udhari | Customer credit balance (retail/wholesale) |
| Serial / IMEI | Unique unit identity |
| Batch / Lot / Expiry | Generic inventory concepts (not pharmacy) |

**Do not use:** Medical Store, Medicine, Prescription as product features.
""",
)

w(
    "00-overview/requirements-traceability.md",
    """
# Requirements Traceability

Every industry requirement should map:

```
Requirement ID
  → Feature
  → Module
  → Database Entity
  → API Endpoint
  → Frontend Page
  → Test Case
  → Sprint / Phase
```

## Example (Restaurant)

| Layer | Artifact |
|-------|----------|
| Requirement | `REST-REQ-004` Table management |
| Feature | Table Management |
| Module | Restaurant Tables |
| Entity | `RestaurantTable` |
| API | `GET/POST /api/v1/restaurant/tables` |
| UI | Tables page |
| Test | `TEST-REST-001` |
| Sprint | Restaurant pack sprint (see 12-sprints) |

Each business folder contains the linked artifacts (`requirements.md`, `features.md`, … `testing.md`, `roadmap.md`).
""",
)

# Feature matrix
headers = [
    "Feature",
    "Restaurant",
    "Cafe",
    "Grocery",
    "Clothing",
    "Mobile",
    "Hardware",
    "Bakery",
    "Stationery",
    "Electronics",
    "Furniture",
    "Building",
    "Books",
    "Wholesale",
    "Travel",
]

# C=COMMON I=INDUSTRY O=OPTIONAL N=NOT REQUIRED
rows = [
    ("Billing engine", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"),
    ("Customers", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"),
    ("Inventory qty", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "O"),
    ("Suppliers/Purchase", "O", "O", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "N"),
    ("Expenses", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"),
    ("Tables", "I", "O", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N"),
    ("KOT/Kitchen", "I", "O", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N"),
    ("Recipes", "I", "O", "N", "N", "N", "N", "O", "N", "N", "N", "N", "N", "N", "N"),
    ("Barcode POS", "O", "O", "I", "I", "O", "O", "O", "I", "O", "N", "O", "I", "I", "N"),
    ("Units kg/L/m", "O", "O", "I", "N", "N", "I", "O", "O", "N", "O", "I", "N", "I", "N"),
    ("Customer credit", "O", "O", "I", "O", "O", "I", "O", "I", "O", "O", "I", "O", "I", "N"),
    ("Batch/Expiry", "O", "O", "I", "N", "N", "O", "I", "O", "N", "N", "O", "N", "O", "N"),
    ("Size/Color/Brand", "N", "N", "N", "I", "O", "O", "N", "O", "O", "O", "N", "N", "O", "N"),
    ("IMEI/Serial", "N", "N", "N", "N", "I", "N", "N", "N", "I", "N", "N", "N", "N", "N"),
    ("Warranty/Repair", "N", "N", "N", "N", "I", "N", "N", "N", "I", "N", "N", "N", "N", "N"),
    ("Warehouse/Transfer", "N", "N", "N", "N", "N", "O", "N", "N", "N", "O", "I", "N", "I", "N"),
    ("Quotation/Challan", "N", "N", "N", "N", "N", "O", "N", "N", "N", "I", "I", "N", "I", "N"),
    ("Custom orders", "N", "N", "N", "N", "N", "N", "I", "N", "N", "I", "N", "N", "N", "N"),
    ("Tour packages/Booking", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "I"),
    ("Agent commission", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "I"),
    ("Medical/Prescription", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N"),
]

legend = "C=COMMON · I=INDUSTRY-SPECIFIC · O=OPTIONAL · N=NOT REQUIRED"

matrix_lines = [
    "# Business Feature Matrix",
    "",
    legend,
    "",
    "| " + " | ".join(headers) + " |",
    "|" + "|".join(["---"] * len(headers)) + "|",
]
for r in rows:
    matrix_lines.append("| " + " | ".join(r) + " |")
matrix_lines.append("")
matrix_lines.append("Medical/Prescription row is **N** for all types by product decision.")
w("00-overview/business-feature-matrix.md", "\n".join(matrix_lines))

# Architecture stubs from existing content summaries
arch_files = {
    "01-architecture/system-architecture.md": """
# System Architecture

```
PRABHA BILLING SaaS
  ├── Master Platform (plans, trial, approvals, audit)
  ├── Common Core (billing, inventory, customers, payments, reports, …)
  └── Industry Modules (14 packs)
```

Request path: Frontend → API → AuthN → AuthZ → Tenant resolution → Service → DB → Response.

See also backend/frontend/api docs in this folder. Full narrative: migrated from prior `architecture.md`.
""",
    "01-architecture/backend-architecture.md": """
# Backend Architecture

**Stack:** Flask · SQLAlchemy · MySQL/MariaDB · JWT

Retain: `controllers/ services/ repositories/ models/ routes/ middleware/`

Target extension: `app/core/` (billing/inventory/tax) + `app/modules/{industry}/`

No business logic in routes. Migrations only after approved sprints + backup.
""",
    "01-architecture/frontend-architecture.md": """
# Frontend Architecture

**Stack:** React · Vite · MUI · Axios

Layouts: Auth, Owner, Billing, Master. Paths in `routes/paths.js`.

Target: `src/modules/{industry}/` lazy routes gated by feature flags.

Known issue (documented, not fixed here): Owner↔Billing dual-shell navigation.
""",
    "01-architecture/api-architecture.md": """
# API Architecture

Base: `/api/v1` · Envelope `{ success, data, meta, error }`

Common prefixes exist today: `/auth`, `/master`, `/bills`, `/items`, `/reports`, …

Industry namespaces (future): `/restaurant`, `/cafe`, `/grocery`, … `/travel`

Never authorize using client-supplied `tenant_id`.
""",
    "01-architecture/project-structure.md": """
# Project Structure (target)

```
backend/app/core/ + modules/
frontend/src/modules/
docs/00-overview … 12-sprints + 05-businesses/{01..14}
```

Incremental adoption — no big-bang rewrite.
""",
    "01-architecture/technology-stack.md": """
# Technology Stack

| Layer | Choice |
|-------|--------|
| Backend | Python, Flask, SQLAlchemy |
| DB | MySQL / MariaDB (Hostinger live) |
| Frontend | React, Vite, MUI |
| Auth | JWT + token_version |
| Integrations | SMTP, WhatsApp Cloud API (optional) |
""",
}

for rel, text in arch_files.items():
    w(rel, text)

mt = {
    "02-multi-tenant/tenant-architecture.md": """
# Tenant Architecture

Each approved business is a **tenant**. Shared DB, logical isolation via `tenant_id`.

```
Tenant → Users, Catalog, Bills, Inventory, Settings, Industry data
```

Platform globals: MasterAdmin, Plans, BusinessTypes, Module catalog.
""",
    "02-multi-tenant/tenant-isolation.md": """
# Tenant Isolation

`tenant_id` comes from JWT/session context only. Cross-tenant access → **403/404**.

Test Users, Customers, Products, Bills, Payments, Purchases, Inventory, Expenses, Reports, Notifications, Audit, Settings.

See [../10-testing/tenant-isolation-testing.md](../10-testing/tenant-isolation-testing.md).
""",
    "02-multi-tenant/authentication.md": """
# Authentication

| Actor | Entry |
|-------|-------|
| Business users | `/login` |
| Master Admin | Footer dot → `/master/login` |

JWT; logout/password change bumps `token_version`. Registration does not issue JWT until approve.
""",
    "02-multi-tenant/authorization.md": """
# Authorization

RBAC: OWNER · BILLING_USER · MANAGER (target) + industry roles only when needed.

Guards: `auth_required`, `master_required`, subscription 402 gate, module entitlements.
""",
    "02-multi-tenant/security.md": """
# Security

Password hashing · JWT · CORS · validation · ORM parameterization · rate limits · secrets in env · dual audit ledgers.

Never commit DB/JWT/SMTP/WhatsApp/payment secrets. Privacy/Terms need legal review.
""",
}
for rel, text in mt.items():
    w(rel, text)

master = {
    "03-master-admin/master-admin-overview.md": """
# Master Admin Overview

Prabha Technology operators (`master_admins`). Footer-dot login. Manages approvals, businesses, plans, trial, lifecycle, platform audit/notifications.
""",
    "03-master-admin/business-approval.md": """
# Business Approval

Register → PENDING request → Master Approve/Reject → Tenant + Owner (+ trial if enabled).
""",
    "03-master-admin/business-management.md": """
# Business Management

Activate / Deactivate (tenant login) · Suspend/Resume billing (subscription) · Assign plan · Extend trial · Renew · Cancel. Data never deleted on deactivate.
""",
    "03-master-admin/subscription-management.md": """
# Subscription Management (Master)

States: PENDING, TRIAL, ACTIVE, EXPIRING, EXPIRED, CANCELLED, SUSPENDED. Manual renew; SaaS gateway optional later.
""",
    "03-master-admin/trial-management.md": """
# Trial Management

Configurable `trial_enabled`, `trial_days` (default 15), `expiry_warning_days`. Applies to newly approved businesses.
""",
    "03-master-admin/plan-management.md": """
# Plan Management

CRUD plans; price; features; visibility; active flag; future limits (users/products/invoices). Landing uses `GET /public/plans`.
""",
    "03-master-admin/master-dashboard.md": """
# Master Dashboard

KPIs deep-link to filtered lists (account vs subscription status). Registration queue, trials, plans, businesses, audit, trial settings.
""",
}
for rel, text in master.items():
    w(rel, text)

print("shared sections batch 1 done")
