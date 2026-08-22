# -*- coding: utf-8 -*-
from pathlib import Path

DOCS = Path(__file__).resolve().parent

def w(rel: str, text: str) -> None:
    p = DOCS / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip() + "\n", encoding="utf-8")
    print(rel)

COMMON = {
    "billing.md": """
# Common Module — Billing

**Single reusable billing engine** for all industries.

## Supports

Products · Services · Mixed invoices · Qty/Unit/Price · Discount · CGST/SGST/IGST · Cash/Online/UPI/Card/Credit · Partial/Advance · Returns/Refunds (target) · Print/PDF/WhatsApp

## Industry packs

Document only **extensions** (e.g. KOT→bill, IMEI line, service booking line). Do not fork a second engine.

## Current baseline

`bills` / `bill_items` with cash|online, cancel, PDF, WhatsApp/email exist today.

## Stock rule

Product lines: reject insufficient stock unless setting allows negative. Concurrent-safe checks required.
""",
    "inventory.md": """
# Common Module — Inventory

Flexible engine: simple qty, weight, volume, length, area, serial, batch/lot, expiry, variants.

Operations: receive, adjust, sale deduct, return, transfer, wastage, recipe consume.

**Batch/expiry** are generic (grocery/bakery), not Medical Store features.

Baseline today: `stock_quantity` + `stock_movements`.
""",
    "products.md": """
# Common Module — Products / Items

Catalog items (evolve toward Product + Service). Soft deactivate. SKU/barcode optional. Variants/serials via industry extensions.
""",
    "categories.md": """
# Common Module — Categories

Hierarchical categories with `parent_id` / `parent_key` uniqueness. UX polish planned (create parent/child professionally).
""",
    "customers.md": """
# Common Module — Customers

**Gap today** (only bill customer fields). Target: customer master, history, credit hooks for grocery/wholesale.
""",
    "suppliers.md": """
# Common Module — Suppliers

**Gap today.** Target supplier master for purchase-enabled industries.
""",
    "purchases.md": """
# Common Module — Purchases

**Gap today.** PO / goods receipt feeding inventory engine.
""",
    "expenses.md": """
# Common Module — Expenses

**Gap today.** Expense categories + entries for P&L-style reports.
""",
    "payments.md": """
# Common Module — Payments

Distinguish:

1. **Customer payments** on bills (cash/UPI/card/credit/partial/advance)
2. **SaaS subscription payments** to Prabha (often offline/manual)

Do not mix ledgers.
""",
    "reports.md": """
# Common Module — Reports

Today/week/month/year sales · payments · GST · export. Industry reports live in each business `reports.md`.
""",
    "notifications.md": """
# Common Module — Notifications

Typed in-app events (low stock, subscription expiry, …). Tenant + platform channels. Rule-driven where possible.
""",
    "audit-logs.md": """
# Common Module — Audit Logs

Tenant `audit_logs` + platform `platform_audit_logs`. Item activity visible to Owner. No secrets in snapshots.
""",
    "printing.md": """
# Common Module — Printing

Browser/print route for invoices. Industry templates may add table/KOT fields without replacing core print pipeline.
""",
    "pdf-invoices.md": """
# Common Module — PDF Invoices

Server-generated bill PDF. Reused across industries; optional template variants later.
""",
    "whatsapp-integration.md": """
# Common Module — WhatsApp

Per-tenant encrypted config · bill delivery · webhooks. Extend to quotations/bookings via templates.
""",
    "ai-assistant.md": """
# Common Module — AI Assistant

Tenant-scoped insights only; no invented metrics; industry-aware prompts as data exists. Never cross-tenant.
""",
}
for name, text in COMMON.items():
    w(f"04-common-modules/{name}", text)

DB = {
    "database-overview.md": """
# Database Overview

**Live (today):** 23 application tables + `alembic_version` — see historical `07-database-design.md` via [../99-historical/README.md](../99-historical/README.md).

**V2 conceptual:** Common tables + business-specific tables. **No migrations in documentation phase.**
""",
    "database-architecture.md": """
# Database Architecture (Conceptual)

Shared MySQL/MariaDB · logical multi-tenancy · DECIMAL money · soft-cancel financials · append-only audit/stock.

Global: BusinessType, Module, Feature, Plans, MasterAdmin  
Tenant: Users, Products, Bills, Industry entities  

Medical/prescription entities are forbidden.
""",
    "common-tables.md": """
# Common Tables (Conceptual + Current)

| Area | Current / Target |
|------|------------------|
| Tenancy | tenants, users, roles |
| Catalog | categories, items→products |
| Sales | bills, bill_items, bill_number_counters |
| Stock | stock_movements |
| Delivery | bill_deliveries, tenant_whatsapp_configs |
| Ops | notifications, audit_logs |
| SaaS | master_admins, registration_requests, plans, subscriptions, … |
| Target gaps | customers, suppliers, payments, purchases, expenses, warehouses |
""",
    "business-specific-tables.md": """
# Business-Specific Tables (Conceptual Index)

| Business | Example entities |
|----------|------------------|
| Restaurant | RestaurantTable, KOT, Recipe, WastageEntry |
| Cafe | MenuAddOn, ComboOffer |
| Grocery | CustomerCreditAccount, BulkPriceTier |
| Clothing | Size, Color, Brand, ProductVariant |
| Mobile | SerialUnit, Warranty, RepairTicket |
| Hardware | UnitOfMeasure, PriceHistory |
| Bakery | ProductionBatch, CakeOrder |
| Stationery | Brand, ProductBarcode |
| Electronics | SerialUnit, InstallationJob |
| Furniture | CustomOrder, Quotation, DeliveryJob |
| Building | Warehouse, DeliveryChallan, StockTransfer |
| Books | BookMetadata |
| Wholesale | SalesOrder, PurchaseOrder, CustomerPriceList |
| Travel | TourPackage, Booking, AgentCommission |

Details: each `05-businesses/*/database.md`.
""",
    "relationships.md": """
# Relationships

Tenant 1—N all tenant entities (RESTRICT). Bill 1—N BillItem. Product 1—N Variant/Serial/Batch. BusinessType M—N Module.

Live FK details remain in historical relationship docs until V2 migrations.
""",
    "indexes.md": """
# Indexes (Guidelines)

Always index `(tenant_id, …)` on hot tables. Unique per tenant: email, SKU, bill_number, IMEI/ISBN as applicable. Follow `parent_key` pattern for nullable hierarchy uniques.
""",
    "tenant-data-model.md": """
# Tenant Data Model

```
Tenant
 ├── Users / Roles
 ├── Catalog / Customers / Suppliers
 ├── Bills / Payments
 ├── Inventory
 └── Industry pack tables
```

Platform tables have no tenant ownership (or optional tenant_id on audit only).
""",
    "er-diagrams.md": """
# ER Diagrams

```mermaid
erDiagram
  TENANT ||--o{ BILL : has
  BILL ||--|{ BILL_ITEM : contains
  TENANT ||--o{ PRODUCT : has
  BUSINESS_TYPE ||--o{ TENANT : classifies
```

Per-industry diagrams: see each business `database.md` + workflow mermaid.
""",
    "migration-strategy.md": """
# Migration Strategy

1. Backup + inspect  
2. Additive Alembic/helpers only  
3. Map legacy `business_type` strings → 14-type catalog  
4. Never `02_schema.sql` on live  
5. Stamp after helpers on Hostinger MariaDB  
6. No DROP/DELETE production data without explicit approval  

Documentation phase creates **zero** migrations.
""",
}
for name, text in DB.items():
    w(f"06-database/{name}", text)

API = {
    "common-apis.md": """
# Common APIs

Existing: `/auth`, `/tenants`, `/categories`, `/items`, `/bills`, `/stock-movements`, `/reports`, `/notifications`, `/audit-logs`, `/ai`, `/public/plans`.

Target additions: `/customers`, `/suppliers`, `/payments`, `/purchases`, `/expenses`, `/inventory`, `/modules/me`.
""",
    "authentication-apis.md": """
# Authentication APIs

`POST /auth/login` · `register-business` · `logout` · `change-password` · forgot/reset/verify · `GET /auth/me`
""",
    "billing-apis.md": """
# Billing APIs

`POST/GET /bills` · cancel · pdf · print · send-whatsapp · today-summary. Industry packs may POST helper endpoints that create bills via the same engine.
""",
    "inventory-apis.md": """
# Inventory APIs

`POST /items/{id}/adjust-stock` · `receive-stock` · `GET /stock-movements`. Future: batches, serials, warehouses under `/inventory`.
""",
    "report-apis.md": """
# Report APIs

`/reports/summary` · daily/weekly/monthly/custom · export. Industry metrics may add scoped report routes.
""",
    "master-admin-apis.md": """
# Master Admin APIs

`/master/dashboard/summary` · registration-requests · plans · businesses (`status`, `tenant_status`) · trials · settings/trial · audit-logs · notifications · jobs/expiry-check.
""",
    "business-apis.md": """
# Business (Industry) APIs

Namespaces per pack: `/restaurant`, `/cafe`, `/grocery`, `/clothing`, `/mobile`, `/hardware`, `/bakery`, `/stationery`, `/electronics`, `/furniture`, `/building-material`, `/books`, `/wholesale`, `/travel`.

See each `05-businesses/*/api.md`. Register blueprints only when that sprint starts.
""",
}
for name, text in API.items():
    w(f"07-api/{name}", text)

UI = {
    "design-system.md": """
# Design System

Professional SaaS using MUI. Consistent spacing/typography. Avoid excessive cards, gradients, oversized CTAs, AI-generic layouts.
""",
    "layout-guidelines.md": """
# Layout Guidelines

Clear page hierarchy · one primary action · tables for dense data · dialogs for confirms · empty/loading/error states required.
""",
    "responsive-design.md": """
# Responsive Design

Mobile-first usable POS where needed. Breakpoints via MUI. Test Owner/Billing/Master shells on narrow screens.
""",
    "dark-mode.md": """
# Dark Mode

Existing theme toggle; persist per device. Industry pages must respect theme tokens.
""",
    "common-components.md": """
# Common Components

PageShell · FilterBar · PaginationBar · TableCard · KpiCard · EmptyState · TruncateText · SubscriptionLockout · Notification bells.
""",
    "navigation.md": """
# Navigation

Type-aware nav from module registry. Master: footer-dot entry. **Known issue:** Owner→Billing unmounts Owner shell; return via Owner Dashboard — fix in UX sprint.
""",
}
for name, text in UI.items():
    w(f"08-ui-ux/{name}", text)

SUB = {
    "subscription-overview.md": """
# Subscription Overview

SaaS entitlement separate from shop customer payments. Gate billing APIs with 402 when locked.
""",
    "plans.md": """
# Plans

Master-managed catalog; dynamic landing prices; features/limits; deactivate hides from public without rewriting `price_at_purchase`.
""",
    "free-trial.md": """
# Free Trial

Default 15 days; Master can disable or change days; applies on approve when enabled.
""",
    "expiry-notifications.md": """
# Expiry Notifications

Warning window (default 5 days) notifies Owner and Master. Idempotent notice log.
""",
    "billing-for-subscription.md": """
# Billing for Subscription (SaaS fee)

Offline/contact or future gateway. Manual renew in Master today. Do not confuse with `/bills` customer invoicing.
""",
}
for name, text in SUB.items():
    w(f"09-subscription/{name}", text)

TEST = {
    "testing-strategy.md": """
# Testing Strategy

Pytest (venv, `FLASK_ENV=testing`) · frontend build · manual UAT · isolation · security · regression. Template in each business `testing.md`.
""",
    "integration-testing.md": """
# Integration Testing

Frontend ↔ API ↔ DB for CRUD of touched modules. Verify envelope and status codes.
""",
    "security-testing.md": """
# Security Testing

Auth matrix · role checks · secret leakage · rate limits · XSS/SQLi via normal inputs.
""",
    "tenant-isolation-testing.md": """
# Tenant Isolation Testing

Tenant A vs B for every new resource. Expect 403/404. Include industry IDs.
""",
    "performance-testing.md": """
# Performance Testing

Paginated lists · indexed tenant queries · bill list without N+1 · POS latency targets set per sprint.
""",
    "regression-testing.md": """
# Regression Testing

Full pytest before sprint close. Re-run Master registration/trial/bill smoke after industry merges.
""",
}
for name, text in TEST.items():
    w(f"10-testing/{name}", text)

print("batch2 done")
