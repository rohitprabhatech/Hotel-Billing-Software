# Furniture Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-FURN-001 | Create quotation | Tenant type=furniture; user logged in | Execute create quotation | Totals | P0 |
| TEST-FURN-002 | Convert to order | Tenant type=furniture; user logged in | Execute convert to order | Linked | P0 |
| TEST-FURN-003 | Advance payment | Tenant type=furniture; user logged in | Execute advance payment | Balance due | P0 |
| TEST-FURN-004 | Delivery complete | Tenant type=furniture; user logged in | Execute delivery complete | Status | P0 |
| TEST-FURN-005 | Cross-tenant | Tenant type=furniture; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-FURN-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
