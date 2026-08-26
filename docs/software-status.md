# Software Status

**Product:** Business Billing (Prabha Technology Pvt. Ltd.)  
**Purpose:** Living snapshot of **what is actually implemented in code** — not documentation plans alone.

| Field | Value |
|-------|--------|
| **Last updated** | 2026-08-26 |
| **Current sprint** | **Program complete** (BIZ-01 … BIZ-68) — pending business go-live sign-off |
| **Alembic head** | `20260826_biz66_perf_indexes` |

---

## How much is done

| Metric | Count | Notes |
|--------|------:|-------|
| BIZ sprints total | 68 | Industry backlog BIZ-01 … BIZ-68 |
| Completed (code-verified) | **68** | BIZ-01 … BIZ-68 |
| Partially completed | **0** | — |
| Not implemented | **0** | — |
| **Rough progress** | **100%** | 68 ÷ 68 |

Platform foundation (auth, multi-tenant billing, Master Admin, subscriptions, WhatsApp/PDF, etc.) remains live baseline.

---

## Maintenance rule (update after every sprint)

After finishing any BIZ sprint, update this file per the checklist in the previous version (dates, counts, businesses, sprint rows, common platform if changed).

Related: [`14-sprints/sprint-tracker.md`](./14-sprints/sprint-tracker.md)

---

## Supported businesses (14 — Medical Store excluded)

| # | Business | Core billing | Special features in code | Status |
|---|----------|--------------|--------------------------|--------|
| 1 | Hotels / Restaurants | Yes | Full F&B pack | IMPLEMENTED |
| 2 | Cafes / Tea Shops | Yes | Cafe POS + shared F&B | IMPLEMENTED |
| 3 | Grocery / Kirana | Yes | Barcode POS, bulk, batch, credit | IMPLEMENTED |
| 4 | Clothing Shops | Yes | Variants, images, returns | IMPLEMENTED |
| 5 | Mobile Shops | Yes | Serial/IMEI, warranty, accessories, returns/exchange, repairs, brand/model, reports | IMPLEMENTED |
| 6 | Electronics Shops | Yes | Serial/IMEI, warranty, accessories, returns, repairs, brand/model, installation | IMPLEMENTED |
| 7 | Hardware Stores | Yes | UoM POS, quotes/challans, transport, trade credit | IMPLEMENTED (Phase 06 gate) |
| 8 | Building Material | Yes | UoM, quotes/challans, transport, credit, warehouses | IMPLEMENTED (Phase 06 gate) |
| 9 | Bakery / Sweet Shops | Yes | Recipes, production, batch/expiry, cake orders + advances, wastage | IMPLEMENTED (Phase 07 gate) |
| 10 | Stationery Shops | Yes | Search-first barcode POS, bulk pricing, customer credit | IMPLEMENTED (Phase 08 gate) |
| 11 | Book Stores | Yes | ISBN/author/publisher, barcode POS, returns/exchange | IMPLEMENTED (Phase 08 gate) |
| 12 | Furniture Shops | Yes | Attributes, custom orders, delivery board, install, quotations | IMPLEMENTED (Phase 09 gate) |
| 13 | Wholesale Shops | Yes | Price lists, SO/PO, warehouses, aged outstanding, challans, tax invoice, POS, credit | IMPLEMENTED (Phase 10 gate) |
| 14 | Travel Agencies | Yes | Packages, bookings, itinerary/docs, agents + commission | IMPLEMENTED (Phase 11 gate) |

---

## Sprint status (BIZ-01 … BIZ-35 snapshot)

| Sprint | Name | Status |
|--------|------|--------|
| BIZ-01 … BIZ-28 | Platform + F&B + grocery + clothing | COMPLETED |
| BIZ-29 | Serial / IMEI stock | COMPLETED |
| BIZ-30 | Warranty & accessories | COMPLETED |
| BIZ-31 | Serial return/exchange & repairs | COMPLETED |
| BIZ-32 | Mobile brand/model & purchase history | COMPLETED |
| BIZ-33 | Electronics installation tracking | COMPLETED |
| BIZ-34 | Mobile + electronics testing gate | COMPLETED |
| BIZ-35 | Length / weight / area UoM billing | COMPLETED |
| BIZ-36 | Quotations & delivery challans | COMPLETED |
| BIZ-37 | Trade credit & transport charges | COMPLETED |
| BIZ-38 | Warehouse stock foundation | COMPLETED |
| BIZ-39 | Hardware + building material testing gate | COMPLETED |
| BIZ-40 | Bakery production & ingredient inventory | COMPLETED |
| BIZ-41 | Bakery batch expiry & wastage | COMPLETED |
| BIZ-42 | Custom cake orders & advances | COMPLETED |
| BIZ-43 | Bakery testing gate | COMPLETED |
| BIZ-44 | Stationery pack on shared POS | COMPLETED |
| BIZ-45 | Book store metadata (ISBN / author / publisher) | COMPLETED |
| BIZ-46 | Book returns + stationery/books testing gate | COMPLETED |
| BIZ-47 | Furniture product attributes | COMPLETED |
| BIZ-48 | Furniture custom orders & advances | COMPLETED |
| BIZ-49 | Furniture delivery & installation tracking | COMPLETED |
| BIZ-50 | Furniture quotations & Phase 09 testing gate | COMPLETED |
| BIZ-51 | Wholesale pricing matrices | COMPLETED |
| BIZ-52 | Wholesale sales & purchase orders | COMPLETED |
| BIZ-53 | Wholesale multi-warehouse & stock transfer | COMPLETED |
| BIZ-54 | Wholesale outstanding, challan & GST invoice | COMPLETED |
| BIZ-55 | Wholesale testing gate (Phase 10) | COMPLETED |
| BIZ-56 | Travel tour packages | COMPLETED |
| BIZ-57 | Travel bookings & payments | COMPLETED |
| BIZ-58 | Travel itinerary, hotel/vehicle/tickets & documents | COMPLETED |
| BIZ-59 | Travel agent commission | COMPLETED |
| BIZ-60 | Travel agency testing gate (Phase 11) | COMPLETED |
| BIZ-61 | Cross-business reports enhancement | COMPLETED |
| BIZ-62 | AI industry-aware extensions | COMPLETED |
| BIZ-63 | Module notification templates | COMPLETED |
| BIZ-64 | Tenant isolation regression suite | COMPLETED |
| BIZ-65 | Permission and audit completeness | COMPLETED |
| BIZ-66 | Performance indexes & large catalog hardening | COMPLETED |
| BIZ-67 | Industry modules migration & ops runbook | COMPLETED |
| BIZ-68 | Production readiness gate (business modules) | COMPLETED |

---

## Change log

| Date | Note |
|------|------|
| 2026-08-26 | **Final technical audit:** regenerated greenfield `sql/02_schema.sql` (94 tables ↔ models), SQL README, `chk_items_stock` / `chk_roles_name` on models, deferred `bill_items.serial_unit_id` FK, FE `getApiErrorMessage` + New Bill wiring, PageShell overflow hardening. No new Alembic revision (head still `20260826_biz66_perf_indexes`). Branch: `rs/feature/billingV3`. |
| 2026-08-26 | BIZ-68 completed: industry go-live checklist (security/backup/monitoring/scripts/14-type pilots; Medical excluded), gate report, health readiness smoke; tests (4). Program 68/68 pending business sign-off. |
| 2026-08-26 | BIZ-67 completed: industry ops runbook, 56-revision ordered list, stamp/print helpers, dry-run tests (3). No schema change. |
| 2026-08-26 | BIZ-66 completed: Alembic perf indexes, POS catalog max 100, menu cap 500, index/perf docs + light tests (3). Head `20260826_biz66_perf_indexes`. |
| 2026-08-26 | BIZ-65 completed: audit scrub/PII redact, module filters + AuditPage, industry permission matrix, delete-leaves-audit proofs; tests (6). No new migration. |
| 2026-08-26 | BIZ-64 completed: parametrized industry IDOR suite (`-m isolation`), audit scoping + tenant_id body reject, Billing User on tenant B fixture; tests (10). No new migration. |
| 2026-08-26 | BIZ-63 completed: industry notification template registry, `emit_template` + dedupe/cooldown, `GET /notifications/templates`, batch/KOT/repair/travel/credit wired; tests (6). No new migration. |
| 2026-08-26 | BIZ-62 completed: pluggable rule-based industry AI analyzers on `/ai/analysis`, Industry Insights UI; tests (4). No LLM. |
| 2026-08-26 | BIZ-61 completed: `/reports/available` module registry, custom range ≤366d, bills pagination, dynamic Reports hub; tests (4). No new migration. |
| 2026-08-26 | BIZ-60 completed: Phase 11 travel gate — 23 passed (BIZ-56…60); PII doc isolation; report + manual checklist. No new migration. |
| 2026-08-26 | BIZ-59 completed: travel agents, booking agent link, commission calc/report/paid, UI, tests (4). Alembic `20260826_biz59_travel_agent_commission`. |
| 2026-08-26 | BIZ-58 completed: nested itinerary + document metadata on bookings, Owner/Manager write + audit, Details tabs UI, tests (3). Alembic `20260826_biz58_travel_itinerary_documents`. |
| 2026-08-26 | BIZ-57 completed: travel bookings (`TB-#####`), payments, status board, confirm/due notifications, UI, tests (4). Alembic `20260826_biz57_travel_bookings`. |
| 2026-08-26 | BIZ-56 completed: `tour_packages` + linked untracked items, `/travel/packages` CRUD + bill helper, Tour Packages UI, tests (5). Alembic `20260826_biz56_tour_packages`. |
| 2026-08-26 | BIZ-55 gate PASSED (28 tests across BIZ-51…55). Phase 10 closed. Gate report + manual checklist. |
| 2026-08-26 | BIZ-54 completed: aged outstanding report (`/reports/outstanding`), wholesale challan aliases, TAX INVOICE PDF polish, Outstanding Report UI + print, tests (4). No new migration. |
| 2026-08-26 | BIZ-53 completed: wholesale warehouse aliases, transfer pre-validation, per-WH low-stock alerts, sell-from picker on POS/New Bill, Warehouses UX polish, tests (5). No new migration (BIZ-38 reuse). |
| 2026-08-26 | BIZ-52 completed: sales/purchase orders (`SO-#####` / `PO-#####`), convert to bill/purchase, wholesale aliases, UI, tests (5). Alembic `20260826_biz52_sales_purchase_orders`. |
| 2026-08-26 | BIZ-51 completed: `price_lists` / customer assignments, resolver in bills + POS, Price Lists UI, tests (7). Alembic `20260826_biz51_wholesale_price_lists`. |
| 2026-08-26 | BIZ-50 gate PASSED (28 tests across BIZ-47…50). Phase 09 closed. |
| 2026-08-26 | BIZ-49 completed: `delivery_jobs` (DL-#####), delivery board API/UI, blocks direct DELIVERED for furniture, installation from custom order, notifications, tests (5). Alembic `20260826_biz49_furniture_delivery_tracking`. |
| 2026-08-26 | BIZ-48 completed: furniture `order_type` on shared custom orders, `/furniture/custom-orders` aliases, Furniture Orders board, advance/status tests (5). No new migration. |
| 2026-08-26 | BIZ-47 completed: furniture L/W/H + material/color on items, module `furniture_attributes`, Items UI, search, tests (5). Alembic `20260826_biz47_furniture_product_attributes`. |
| 2026-08-26 | BIZ-46 gate PASSED (20 tests across BIZ-44…46). Book RETURN/EXCHANGE proven; ReturnsPage plain-item exchange catalog. Gate report + manual checklist. Phase 08 closed. |
| 2026-08-26 | BIZ-45 completed: `isbn`/`author`/`publisher` on items, unique ISBN/tenant, search + `/books` aliases, Items UI, tests (5). Alembic `20260826_biz45_book_store_metadata`. |
| 2026-08-26 | BIZ-44 completed: stationery thin pack — `/stationery` POS aliases, search-first StationeryPos UI (owner + billing), module flags, tests (4). No new migration. |
| 2026-08-26 | BIZ-43 gate PASSED (25 tests across BIZ-40…43). Gate report + manual checklist published. Phase 07 closed. |
| 2026-08-25 | BIZ-42 completed: shared `custom_product_orders` (type=bakery), advances, status board, Cake Orders UI, `/custom-orders` + bakery aliases, tests (5). Alembic `20260825_biz42_custom_product_orders`. |
| 2026-08-25 | BIZ-41 completed: bakery batch/expiry enablement, production→batch with expiry, wastage FEFO incl. expired, `/bakery/expiry` alias, tests (6). |
| 2026-08-25 | BIZ-40 completed: production runs (PR-#####) consume recipe BOM / increase FG stock; sell skips recipe expand when production module on; Owner Production UI; tests (6). Alembic `20260825_biz40_bakery_production_runs`. |
| 2026-08-25 | BIZ-39 gate PASSED (27 tests across BIZ-35…39). Gate report + manual checklist published. Phase 06 closed. |
| 2026-08-25 | BIZ-38 completed: warehouses + balances + transfers (ST-#####), bill warehouse_id sell-from, default MAIN seed, Owner Warehouses UI, tests. Alembic `20260825_biz38_warehouse_stock_foundation`. |
| 2026-08-25 | BIZ-37 completed: transport on bills/challans (non-GST), supplier ledger outstanding/pay, credit purchase posting, Credit UI supplier tab, Hardware POS transport. Alembic `20260825_biz37_transport_supplier_credit`. |
| 2026-08-25 | BIZ-36 completed: quotations + delivery challans (convert→bill, challan PDF), Owner UI, hardware modules enabled, wholesale reuse, tests. Alembic `20260825_biz36_quotations_delivery_challans`. |
| 2026-08-25 | BIZ-35 completed: `sale_uom`, measurement UoMs, hardware quote/convert/POS APIs + UI, Decimal stock conversion, tests (pipe 10×450=4500). Alembic `20260825_biz35_sale_uom_measurement`. |
| 2026-08-25 | BIZ-34 gate PASSED (24 tests). Manager repair/install write aligned to `PERM_BILLING`. Gate report + manual checklist published. Phase 05 closed. |
| 2026-08-25 | BIZ-33 completed: installation orders linked to serial sales, schedule board UI, notifications, tests. Alembic `20260825_biz33_installation_orders`. |
| 2026-08-25 | BIZ-32 completed: item brand/model fields, `/mobile/sales` + `/mobile/customer-history`, Items/Reports/Customers UX, tests. Alembic `20260825_biz32_mobile_brand_model`. |
| 2026-08-25 | BIZ-31 completed: serial return/quarantine, serial exchange on bill lines, repair ticket board + API, Returns/Repairs UI, tests. Alembic `20260825_biz31_repairs_serial_exchange`. |
| 2026-08-25 | BIZ-29 completed (POS serial capture, tests). BIZ-30 completed (warranty on bills/print/PDF, accessory links, tests). Work on `rs/feature/billingV3`. |
| 2026-08-25 | Initial software status after audit through partial BIZ-29; merged billingV2 → dev. |
