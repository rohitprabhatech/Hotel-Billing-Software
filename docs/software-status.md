# Software Status

**Product:** Business Billing (Prabha Technology Pvt. Ltd.)  
**Purpose:** Living snapshot of **what is actually implemented in code** — not documentation plans alone.

| Field | Value |
|-------|--------|
| **Last updated** | 2026-08-25 |
| **Current sprint** | **BIZ-31** — Exchange/return & repair (next) |
| **Git branch** | `rs/feature/billingV3` |
| **Alembic head** | `20260825_biz30_warranty_accessories` |

---

## How much is done

| Metric | Count | Notes |
|--------|------:|-------|
| BIZ sprints total | 68 | Industry backlog BIZ-01 … BIZ-68 |
| Completed (code-verified) | **30** | BIZ-01 … BIZ-30 |
| Partially completed | **0** | — |
| Not implemented | **38** | BIZ-31 … BIZ-68 |
| **Rough progress** | **~44%** | 30 ÷ 68 |

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
| 5 | Mobile Shops | Yes | Serial/IMEI, warranty, accessories | IMPLEMENTED |
| 6 | Electronics Shops | Yes | Same as mobile + installation flag (not built) | PARTIAL |
| 7–14 | Others | Yes | Module flags only | PLANNED |

---

## Sprint status (BIZ-01 … BIZ-35 snapshot)

| Sprint | Name | Status |
|--------|------|--------|
| BIZ-01 … BIZ-28 | Platform + F&B + grocery + clothing | COMPLETED |
| BIZ-29 | Serial / IMEI stock | COMPLETED |
| BIZ-30 | Warranty & accessories | COMPLETED |
| BIZ-31 … BIZ-68 | Remaining industry packs | NOT IMPLEMENTED |

---

## Change log

| Date | Note |
|------|------|
| 2026-08-25 | BIZ-29 completed (POS serial capture, tests). BIZ-30 completed (warranty on bills/print/PDF, accessory links, tests). Work on `rs/feature/billingV3`. |
| 2026-08-25 | Initial software status after audit through partial BIZ-29; merged billingV2 → dev. |
