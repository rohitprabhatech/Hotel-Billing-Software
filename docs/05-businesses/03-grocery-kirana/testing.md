# Grocery Stores / Kirana — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-GROC-001 | Barcode lookup | Tenant type=grocery_kirana; user logged in | Scan barcode / `GET /items/by-barcode` | Correct product | P0 |
| TEST-GROC-002 | Sell by kg | Tenant type=grocery_kirana; user logged in | Bill with decimal qty on kg item | Qty/unit correct | P0 |
| TEST-GROC-003 | Credit sale | Tenant type=grocery_kirana; user logged in | Grocery POS credit bill / `POST /bills` payment_method=credit | Ledger + stock updated | P0 |
| TEST-GROC-004 | Credit payment | Tenant type=grocery_kirana; user logged in | `POST /grocery/credit/{id}/pay` | Balance reduces | P0 |
| TEST-GROC-005 | Insufficient stock | Tenant type=grocery_kirana; user logged in | Execute insufficient stock | Blocked | P0 |
| TEST-GROC-006 | Expiry listing | Tenant type=grocery_kirana; batches with expiry | Open Batches / `GET /batches/expiry` | Shows near-expiry + expired | P0 |
| TEST-GROC-007 | Bulk price tier | Tenant type=grocery_kirana; tiers set on item | Bill qty below/at/above min_quantity | Unit price matches tier / base | P0 |
| TEST-GROC-008 | Cross-tenant | Tenant type=grocery_kirana; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-GROC-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Automated gate: `backend/tests/test_biz24_grocery_testing_gate.py` plus BIZ-20…23 files. Sign-off: [`../../14-sprints/biz-24-grocery-gate-report.md`](../../14-sprints/biz-24-grocery-gate-report.md).

Do not run destructive tests on production data.
