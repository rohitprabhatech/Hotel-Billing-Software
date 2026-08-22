# Wholesale Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-WHOL-001 | Customer price applied | Tenant type=wholesale; user logged in | Execute customer price applied | Correct rate | P0 |
| TEST-WHOL-002 | SO → invoice | Tenant type=wholesale; user logged in | Execute so → invoice | Stock move | P0 |
| TEST-WHOL-003 | Warehouse transfer | Tenant type=wholesale; user logged in | Execute warehouse transfer | Balances | P0 |
| TEST-WHOL-004 | Outstanding report | Tenant type=wholesale; user logged in | Execute outstanding report | Matches ledger | P0 |
| TEST-WHOL-005 | Cross-tenant | Tenant type=wholesale; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-WHOL-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
