# BIZ-39 Hardware & Building Material Testing Gate — Sign-Off Report

**Sprint:** BIZ-39 — Hardware and Building Material Testing Gate  
**Phase:** 06 — Hardware / Building Material  
**Date:** 2026-08-25  
**Status:** PASSED

## Purpose

Regression gate after the measurement / trade-docs / credit / warehouse pack (BIZ-35 … BIZ-38). Validates UoM quote billing, quotations & delivery challans (convert + PDF), transport charges, customer/supplier credit, multi-warehouse transfers and sell-from, module matrix, cross-tenant isolation, permissions, audit, and API contracts before Phase 07+.

## Automated Test Evidence

Run from `backend/` with `FLASK_ENV=testing`:

```bash
python -m pytest tests/test_biz35_length_weight_area_uom.py tests/test_biz36_quotation_delivery_challan.py tests/test_biz37_trade_credit_transport.py tests/test_biz38_warehouse_stock_foundation.py tests/test_biz39_hardware_building_material_testing_gate.py -q
```

**Result:** 27 passed (2026-08-25).

| Area | Test file(s) | Gate item |
|------|----------------|-----------|
| BIZ-35 Measurement UoM | `test_biz35_length_weight_area_uom.py` | Pipe quote, sale_uom conversion |
| BIZ-36 Quotes / challans | `test_biz36_quotation_delivery_challan.py` | QT/DC convert → bill, PDF |
| BIZ-37 Credit / transport | `test_biz37_trade_credit_transport.py` | Transport, customer + supplier ledger |
| BIZ-38 Warehouses | `test_biz38_warehouse_stock_foundation.py` | Transfers, sell-from warehouse |
| BIZ-39 Combined gate | `test_biz39_hardware_building_material_testing_gate.py` | Matrix, isolation, contracts |

## Gate Checklist

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Pipe / measurement quote (TEST-HARD-001) | PASS | 10×450 → 4500 via `/hardware/quote` |
| 2 | Hardware POS units + catalog | PASS | Gate + BIZ-35 |
| 3 | Quotation create → convert to bill (TEST-BLDM-002) | PASS | QT-#####; status CONVERTED |
| 4 | Challan create → PDF → convert with transport (TEST-BLDM-003/004) | PASS | DC PDF `%PDF`; transport on bill |
| 5 | Customer credit + transport on bill (TEST-HARD-003) | PASS | Outstanding includes transport |
| 6 | Supplier credit purchase + payment | PASS | Outstanding + `/suppliers/{id}/payments` |
| 7 | Warehouse transfer conserves stock (TEST-BLDM-001) | PASS | MAIN → yard; sell from yard |
| 8 | Hardware has no warehouse module | PASS | 403 on `/warehouses` |
| 9 | Building material has warehouse; hardware has bulk_pricing | PASS | Module matrix |
| 10 | Restaurant 403 for hardware verticals | PASS | units/quotes/challans/warehouses |
| 11 | Cross-tenant quotation isolation (TEST-HARD-ISO / BLDM-ISO) | PASS | 404 on foreign QT |
| 12 | Permission: billing cannot create quote/challan; manager can | PASS | Billing list OK |
| 13 | Audit CREATE_WAREHOUSE / CREATE_STOCK_TRANSFER / CREATE_QUOTATION | PASS | Gate |
| 14 | API success envelopes on hardware/docs/warehouse | PASS | Gate |
| 15 | Challan convert grand_total = goods + transport | PASS | 200 + 50 = 250 |

**Checklist completion:** 15 / 15 (100%)

## Gate Fix Applied During Sign-Off

None — full Phase 06 suite was green on first gate run.

## Waived / Deferred Items

| Item | Risk | Decision |
|------|------|----------|
| Automated responsive UI smoke | Low | Manual checklist |
| Staging migration apply | Ops | Run `flask db upgrade` through BIZ-38 on deploy |
| Low-stock notification (TEST-HARD-004) | Low | Covered by shared notifications elsewhere; not re-gated here |
| Wholesale warehouse enablement | n/a | Deferred to BIZ-53 |

## Manual Frontend Smoke Checklist

See [biz-39-manual-frontend-checklist.md](./biz-39-manual-frontend-checklist.md).

## Sign-Off

Hardware + Building Material pack (BIZ-35 … BIZ-38) plus this testing gate (BIZ-39) is **stable enough to close Phase 06**, subject to deploy migrations and manual UI smoke on the target environment.

**Gate result:** APPROVED — proceed to BIZ-40+ after product approval
