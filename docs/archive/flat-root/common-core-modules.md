# Common Core Modules — Prabha Billing SaaS V2

Classification: **CORE** (always for applicable tenants) · **OPTIONAL** (plan or settings) · **INDUSTRY-SPECIFIC** (typed packs)

---

## Module catalog

| # | Module | Class | Notes / today |
|---|--------|-------|----------------|
| 1 | Authentication | CORE | Exists |
| 2 | Authorization | CORE | Exists (extend Manager + permissions) |
| 3 | Multi-Tenant Management | CORE | Exists |
| 4 | Business Registration | CORE | Exists (pending approve) |
| 5 | Business Profile | CORE | Exists |
| 6 | User Management | CORE | Exists |
| 7 | Role Management | CORE | Expand beyond OWNER/BILLING_USER |
| 8 | Permission Management | CORE | New fine-grained layer |
| 9 | Product / Item Management | CORE | Exists |
| 10 | Category Management | CORE | Exists (UX polish) |
| 11 | Customer Management | CORE | **Gap** (bill fields only) |
| 12 | Supplier Management | CORE | **Gap** |
| 13 | Billing | CORE | Exists → engine |
| 14 | Invoice Management | CORE | Exists (history/print/PDF) |
| 15 | Payment Management | CORE | Partial (cash/online) → expand |
| 16 | Inventory Management | CORE | Partial stock → engine |
| 17 | Purchase Management | CORE | **Gap** |
| 18 | Expense Management | CORE | **Gap** |
| 19 | Sales Reports | CORE | Exists |
| 20 | Dashboard | CORE | Exists → type-aware |
| 21 | Notifications | CORE | Exists |
| 22 | Audit Logs | CORE | Exists |
| 23 | Subscription Management | CORE | Exists (platform) |
| 24 | Trial Management | CORE | Exists |
| 25 | Master Admin | CORE | Exists (platform) |
| 26 | AI Business Assistant | OPTIONAL | Exists (extend industries) |
| 27 | WhatsApp Integration | OPTIONAL | Exists |
| 28 | Settings | CORE | Exists |
| 29 | GST / Tax | CORE | Partial → full GST modes |
| 30 | Invoice Printing | CORE | Exists |
| 31 | Invoice PDF | CORE | Exists |
| 32 | Search | CORE | Exists (lists) |
| 33 | Filtering | CORE | Exists |
| 34 | Pagination | CORE | Exists |
| 35 | Data Export | CORE | Exists (reports) |
| 36 | Backup / Recovery | CORE | Ops docs + scripts |

### Industry-specific (examples)

Tables/KOT/Kitchen · Size/Color · IMEI · Recipe · Cake orders · ISBN · Warehouse transfer · Tour packages — see [industry-modules.md](./industry-modules.md).

---

## Plan-gated optionals

Master plan features / limits may toggle: WhatsApp, AI, max users, max products, branches (future), storage.

---

## Design rule

Industry modules **consume** core services (billing, inventory, customers). They must not fork a second billing stack unless a documented technical exception is approved.
