# Business-Specific Sprint Plan — Overview

**Status:** Planning complete · **Coding:** not started · **Awaiting:** per-sprint approval (`APPROVED SPRINT BIZ-XX`)

---

## 1. Existing functionality analysis

**Already strong in code:** multi-tenant auth, Master Admin, registration approval, plans/trial, categories/items, bills (GST/PDF/print), stock lock + movements, reports, tenant/platform audit, notifications, WhatsApp/email delivery, AI sales analysis, Owner + Billing shells.

**Partial:** customer fields on bills only; `table_number` text; 9 business-type labels (not 14); receive-stock ≠ purchases; plan `features` JSON = marketing.

**Missing in code:** customers/suppliers/purchases/expenses, Manager role, module flags, tables/KOT, variants, IMEI/serial, batches/expiry, credit ledger, warehouses, quotes/challans, travel bookings, etc.

Detail: [business-feature-gap-analysis.md](./business-feature-gap-analysis.md) and [../00-project-foundation/08-existing-system-analysis.md](../00-project-foundation/08-existing-system-analysis.md).

---

## 2. Business feature gap analysis

Canonical file: [business-feature-gap-analysis.md](./business-feature-gap-analysis.md) — tables for common platform + all 14 businesses.

---

## 3. Recommended development phases

See [business-development-phases.md](./business-development-phases.md) (Phases 01–14). Order prioritizes **shared foundations** and **reusable modules** over cloning 14 apps.

---

## 4. Complete sprint list

**68 sprints:** `sprint-biz-01-…` … `sprint-biz-68-…`

| Range | Focus |
|---|---|
| BIZ-01–10 | Platform readiness (types, flags, Manager, CRM, suppliers, purchases, expenses, barcode/UoM, credit, gate) |
| BIZ-11–19 | Restaurant/Cafe (menu, tables, orders, KOT, settle, recipes, cafe pack, F&B reports, gate) |
| BIZ-20–24 | Grocery |
| BIZ-25–28 | Clothing |
| BIZ-29–34 | Mobile/Electronics (shared serials) |
| BIZ-35–39 | Hardware/Building Material |
| BIZ-40–43 | Bakery |
| BIZ-44–46 | Stationery/Books |
| BIZ-47–50 | Furniture |
| BIZ-51–55 | Wholesale |
| BIZ-56–60 | Travel |
| BIZ-61–63 | Cross reports/AI/notifications |
| BIZ-64–66 | Security/audit/performance |
| BIZ-67–68 | Production readiness |

Platform docs sprints `sprint-00`…`sprint-14` remain historical foundation plan (much already built). **Active industry plan = BIZ-***.

---

## 5. Sprint dependencies

```
BIZ-01 → BIZ-02 → …
BIZ-01…09 → BIZ-10 (Phase 01 gate)
BIZ-10 → BIZ-11…19 (F&B)
BIZ-10 + BIZ-08/09 → BIZ-20…24 (Grocery)
BIZ-10 → BIZ-25…28 (Clothing)
BIZ-10 + returns → BIZ-29…34 (Serial verticals)
BIZ-10 + UoM/credit → BIZ-35…39
BIZ-16 + BIZ-22 → BIZ-40…43 (Bakery)
Grocery-like → BIZ-44…46
Custom orders + quotes → BIZ-47…50
Pricing + WH + docs → BIZ-51…55
CRM → BIZ-56…60
Vertical gates → BIZ-61…63 → BIZ-64…66 → BIZ-67…68
```

Tracker: [sprint-tracker.md](./sprint-tracker.md).

---

## 6. Database impact summary (conceptual — no SQL)

| Class | Examples | Isolation |
|---|---|---|
| Common new | `customers`, `suppliers`, `purchases`, `purchase_items`, `expenses`, module flag tables | `tenant_id` from JWT |
| Shared industry | `dining_tables`, `orders`, `kots`, `item_variants`, `serial_units`, `item_batches`, `party_ledger_entries`, `warehouses`, `quotations`, `custom_product_orders` | same |
| Vertical-only | `tour_packages`, `travel_bookings`, `travel_agents`, `repair_orders`, `installation_orders` | same |
| Extend existing | `items` (barcode, uom, track_serial), `bills` (customer_id, service_charge, order_id) | same |

**Every tenant-owned entity:** `tenant_id` required; unique constraints include tenant; never trust client `tenant_id`.

---

## 7. API impact summary (conceptual)

New groups (examples): `/customers`, `/suppliers`, `/purchases`, `/expenses`, `/tables`, `/orders`, `/kots`, `/variants`, `/serial-units`, `/batches`, `/ledger`, `/warehouses`, `/quotations`, `/challans`, `/custom-orders`, `/travel-bookings`, `/modules`.

Extend: `/items`, `/bills`, `/reports`, `/users` (Manager), `/tenants/business-types`.

Guards: module flags + roles; stock validation retained on settle/sale.

---

## 8. Frontend impact summary

New Owner/Billing pages per module; **same MUI design system** (nav filtered by modules). No separate visual language per business. Kitchen/POS layouts may densify controls but keep tokens/spacing/typography.

---

## 9. Reusable module analysis

| Module | Used by |
|---|---|
| Feature flags | All |
| Customers + credit ledger | Grocery, Hardware, Stationery, Wholesale, Building, Travel, … |
| Barcode + UoM | Grocery, Stationery, Clothing, Hardware, Books, Wholesale |
| Tables + KOT + orders | Restaurant, Cafe |
| Recipes / ingredients | Restaurant, Bakery |
| Batches / expiry / wastage | Grocery, Bakery, F&B |
| Variants | Clothing (+ hardware variants) |
| Serial / IMEI | Mobile, Electronics |
| Returns / exchange | Clothing, Mobile, Electronics, Books |
| Quotations / challans | Building, Wholesale, Furniture, Hardware |
| Warehouses / transfers | Building, Wholesale |
| Custom orders + advances | Bakery, Furniture |
| Installation / repair | Electronics, Furniture, Mobile |

---

## 10. Business-specific module analysis

| Business | Specific (after shared) |
|---|---|
| Restaurant | Service charge, split bill, waiter (optional), F&B reports |
| Cafe | Add-ons, combos, quick POS |
| Grocery | Fast POS, udhari UX, FEFO policy |
| Clothing | Size/color matrix, images, brand reports |
| Mobile | IMEI UX, model catalog |
| Electronics | Installation jobs |
| Hardware | Pipe/length pricing UX |
| Building | Transport, warehouse emphasis |
| Bakery | Production runs, cake orders |
| Stationery | Thin pack / search POS |
| Books | ISBN/author/publisher |
| Furniture | Dimensions, delivery board |
| Wholesale | Price lists, SO/PO |
| Travel | Packages, bookings, itinerary, commissions |

---

## 11. Security considerations

- JWT tenant context only; IDOR tests per new resource (BIZ-64).  
- Master vs tenant separation unchanged.  
- Manager least privilege (BIZ-03, BIZ-65).  
- Audit old→new for catalog, stock, bills, cancels, returns (BIZ-65).  
- Travel documents = PII — tenant isolation + later encryption note.  
- Stock: never allow oversell when tracked (extend lock pattern).

---

## 12. Testing strategy

Each vertical ends with a **testing gate** sprint. Types: functional, API, DB, tenant isolation, permissions, stock, billing, reports, UI, regression. Cross-cutting: BIZ-64–66. Guides remain under `docs/12-testing-guides/` and `docs/10-testing/`.

---

## 13. Final sprint tracker

[sprint-tracker.md](./sprint-tracker.md) — all BIZ sprints **NOT STARTED**.

---

## Review process

1. Review sprints one by one.  
2. Say **`APPROVED SPRINT BIZ-XX`** to approve for future development.  
3. Say **`CHANGE SPRINT BIZ-XX`** to revise that sprint (and declare dependent doc updates).  
4. **Do not start coding** until approval.
