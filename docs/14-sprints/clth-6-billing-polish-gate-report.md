# CLTH-6 Clothing Billing Polish — Sign-Off Report

**Sprint:** CLTH-6 — Testing gate + regression (billing polish phase)  
**Branch:** `rs/feature/cloth`  
**Date:** 2026-08-28  
**Status:** PASSED (automated)

## Scope

Frontend billing polish (CLTH-1 … CLTH-5) on top of backend pack BIZ-25 … BIZ-28:

| Sprint | Deliverable |
|--------|-------------|
| CLTH-1 | Nav + isolation (`clothingBillingUserNav`, Sell section) |
| CLTH-2 | `ClothingBillingHome` dashboard |
| CLTH-3 | Barcode variant POS (`barcode_pos` + `matched_variant`) |
| CLTH-4 | Owner dashboard widgets (sizes/colors, low variants, returns) |
| CLTH-5 | POS polish (customer, print/WhatsApp, category filter, mobile) |
| CLTH-6 | Automated gate + hotel/cafe regression |

## Automated Test Evidence

Run from `backend/` with `FLASK_ENV=testing`:

```bash
python -m pytest tests/test_biz25_clothing_variants.py tests/test_biz26_clothing_images_pos.py tests/test_biz27_clothing_returns.py tests/test_biz28_clothing_reports_and_testing_gate.py tests/test_clth_billing_polish_gate.py -q
```

**Clothing gate result:** 30 passed (2026-08-28) — BIZ-25…28 (25) + CLTH-6 (5).

**Hotel / cafe regression** (tenants must stay isolated):

```bash
python -m pytest tests/test_biz19_restaurant_cafe_testing_gate.py tests/test_cafe_stock_sprint6.py -q
```

**Result:** 14 passed (2026-08-28).

## Gate Checklist

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | BIZ-25 … BIZ-28 backend gate | PASS | Variants, POS, returns, reports |
| 2 | Clothing sales `period` param (dashboard) | PASS | `test_clth_billing_polish_gate` |
| 3 | Bill with `customer_id` from POS | PASS | CLTH-5 customer picker |
| 4 | Barcode → `matched_variant` | PASS | CLTH-3 scan path |
| 5 | Switch clothing → hotel_restaurant | PASS | Tables API works; clothing 403 |
| 6 | Cafe tenant clothing endpoints | PASS | 403; cafe catalog 200 |
| 7 | F&B gate (BIZ-19) | PASS | No bleed from clothing work |
| 8 | Cafe linked stock (Sprint 6) | PASS | Hotel recipe regression |

## Manual Frontend Smoke

See [clth-manual-frontend-checklist.md](./clth-manual-frontend-checklist.md) (extends BIZ-28 checklist with CLTH-1 … CLTH-5 items).

## Sign-Off

Clothing **billing polish phase** (CLTH-1 … CLTH-6) is **ready for merge review** on `rs/feature/cloth`, subject to manual UI smoke on the target environment.

**Gate result:** APPROVED — automated
