# Business Development Phases

**Purpose:** When we build industry capability (not “what each business needs” — that lives under `docs/05-businesses/`).

## Why this phase order (vs a naive 14-business list)

Code analysis shows the **common SaaS core already runs** (auth, tenancy, Master Admin, bills, stock validation, WhatsApp, AI, audit). The largest blockers for *all* verticals are shared: **CRM, suppliers, purchases, expenses, module flags, 14-type catalog, Manager role**.

Therefore:

1. **Phase 01 first** — Common Platform Readiness (gap-fill, not rebuild).  
2. **Restaurant/Cafe next** — hardest workflow (orders/KOT) and unlocks shared F&B modules.  
3. **Grocery** — establishes barcode/UoM/credit/expiry used by many retail packs.  
4. **Clothing → Mobile/Electronics** — variants then serials (two inventory paradigms).  
5. **Hardware/Building** — measurement + documents + warehouses (feeds wholesale).  
6. **Bakery** — reuses recipes/batches/custom orders.  
7. **Stationery/Books** — mostly configuration on shared POS.  
8. **Furniture** — reuses custom orders/quotes/delivery.  
9. **Wholesale** — composes pricing + SO/PO + warehouses.  
10. **Travel last among verticals** — service/booking model differs from SKU stock.  
11. **Cross reports/AI/notifications** after packs exist.  
12. **Security/perf then production**.

Medical Store remains **out of scope permanently**.

| Phase | Name | Primary sprints | Depends on |
|---|---|---|---|
| 01 | Common Platform Readiness | BIZ-01 … BIZ-10 | Existing production baseline |
| 02 | Restaurant / Cafe | BIZ-11 … BIZ-19 | Phase 01 gate |
| 03 | Grocery / Retail | BIZ-20 … BIZ-24 | Phase 01 (+ shared barcode/credit) |
| 04 | Clothing | BIZ-25 … BIZ-28 | Phase 01 |
| 05 | Mobile / Electronics | BIZ-29 … BIZ-34 | Phase 01 (+ returns) |
| 06 | Hardware / Building Material | BIZ-35 … BIZ-39 | Phase 01 (+ UoM/credit) |
| 07 | Bakery / Food Production | BIZ-40 … BIZ-43 | Recipes (Phase 02) + batches (Phase 03) |
| 08 | Stationery / Books | BIZ-44 … BIZ-46 | Grocery-like shared POS |
| 09 | Furniture | BIZ-47 … BIZ-50 | Custom orders + quotes |
| 10 | Wholesale | BIZ-51 … BIZ-55 | Pricing + warehouse + docs |
| 11 | Travel Agency | BIZ-56 … BIZ-60 | CRM + payments patterns |
| 12 | Cross-Business Reports / AI / Notifications | BIZ-61 … BIZ-63 | Vertical gates |
| 13 | Security / Testing / Performance | BIZ-64 … BIZ-66 | Phase 12 |
| 14 | Production Readiness | BIZ-67 … BIZ-68 | Phase 13 |

See also: [business-feature-gap-analysis.md](./business-feature-gap-analysis.md) · [sprint-tracker.md](./sprint-tracker.md) · [business-sprint-plan-overview.md](./business-sprint-plan-overview.md)
