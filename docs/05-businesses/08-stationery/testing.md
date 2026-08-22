# Stationery Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-STAT-001 | Search product | Tenant type=stationery; user logged in | Execute search product | Relevant hits | P0 |
| TEST-STAT-002 | Barcode bill | Tenant type=stationery; user logged in | Execute barcode bill | Correct item | P0 |
| TEST-STAT-003 | Bulk price | Tenant type=stationery; user logged in | Execute bulk price | Tier applied | P0 |
| TEST-STAT-004 | Low stock alert | Tenant type=stationery; user logged in | Execute low stock alert | Fires | P0 |
| TEST-STAT-005 | Cross-tenant | Tenant type=stationery; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-STAT-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
