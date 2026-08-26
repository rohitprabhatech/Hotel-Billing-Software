# Stationery Shops — Testing

## Automated (BIZ-44)

Suite: `backend/tests/test_biz44_stationery_pack.py` (4 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_stationery_module_flags` | barcode_pos, bulk_pricing, customer_credit on; no batch/serial |
| `test_stationery_pos_catalog_and_search` | catalog, search, by-barcode |
| `test_stationery_barcode_bill_and_credit` | cash + credit bill, stock, outstanding |
| `test_stationery_forbidden_for_restaurant` | 403 when not stationery |

## Automated (Phase 08 gate — BIZ-46)

Full suite BIZ-44 … BIZ-46 — **20 passed** (2026-08-26). See [biz-46-stationery-books-gate-report.md](../../14-sprints/biz-46-stationery-books-gate-report.md).

## Manual smoke

| Test ID | Purpose | Expected | Priority |
|---------|---------|----------|----------|
| TEST-STAT-001 | Search product on Stationery POS | Hits by name/SKU | P0 |
| TEST-STAT-002 | Barcode / Enter add to cart + cash bill | Correct item & stock ↓ | P0 |
| TEST-STAT-003 | Bulk price tier on qty | Tier rate on bill | P0 |
| TEST-STAT-004 | Credit checkout + Credit page | Outstanding updates | P0 |
| TEST-STAT-005 | Restaurant tenant hits `/stationery/*` | 403 | P0 |

## Isolation

| TEST-STAT-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
