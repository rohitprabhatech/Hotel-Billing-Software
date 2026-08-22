# Clothing Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-CLTH-001 | Create variant | Tenant type=clothing; user logged in | Execute create variant | Size+color stock row | P0 |
| TEST-CLTH-002 | Sell variant | Tenant type=clothing; user logged in | Execute sell variant | Only that stock reduces | P0 |
| TEST-CLTH-003 | Wrong size blocked | Tenant type=clothing; user logged in | Execute wrong size blocked | Validation | P0 |
| TEST-CLTH-004 | Exchange | Tenant type=clothing; user logged in | Execute exchange | Stock in/out correct | P0 |
| TEST-CLTH-005 | Brand report | Tenant type=clothing; user logged in | Execute brand report | Totals match | P0 |
| TEST-CLTH-006 | Cross-tenant SKU | Tenant type=clothing; user logged in | Execute cross-tenant sku | 403/404 | P0 |

## Isolation

| TEST-CLTH-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
