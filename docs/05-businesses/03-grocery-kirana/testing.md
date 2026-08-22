# Grocery Stores / Kirana — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-GROC-001 | Barcode lookup | Tenant type=grocery_kirana; user logged in | Scan barcode / `GET /items/by-barcode` | Correct product | P0 |
| TEST-GROC-002 | Sell by kg | Tenant type=grocery_kirana; user logged in | Bill with decimal qty on kg item | Qty/unit correct | P0 |
| TEST-GROC-003 | Credit sale | Tenant type=grocery_kirana; user logged in | Execute credit sale | Ledger updated | P0 |
| TEST-GROC-004 | Credit payment | Tenant type=grocery_kirana; user logged in | Execute credit payment | Balance reduces | P0 |
| TEST-GROC-005 | Insufficient stock | Tenant type=grocery_kirana; user logged in | Execute insufficient stock | Blocked | P0 |
| TEST-GROC-006 | Expiry listing | Tenant type=grocery_kirana; user logged in | Execute expiry listing | Shows near-expiry | P0 |
| TEST-GROC-007 | Bulk price tier | Tenant type=grocery_kirana; user logged in | Execute bulk price tier | Unit price changes | P0 |
| TEST-GROC-008 | Cross-tenant | Tenant type=grocery_kirana; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-GROC-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
