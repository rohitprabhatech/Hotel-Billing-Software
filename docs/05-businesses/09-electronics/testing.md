# Electronics Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-ELEC-001 | Sell serial | Tenant type=electronics; user logged in | Execute sell serial | Marked sold | P0 |
| TEST-ELEC-002 | Warranty auto-create | Tenant type=electronics; user logged in | Execute warranty auto-create | OK | P0 |
| TEST-ELEC-003 | Install job | Tenant type=electronics; user logged in | Execute install job | Status flow | P0 |
| TEST-ELEC-004 | Return serial | Tenant type=electronics; user logged in | Execute return serial | Restock rules | P0 |
| TEST-ELEC-005 | Cross-tenant | Tenant type=electronics; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-ELEC-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
