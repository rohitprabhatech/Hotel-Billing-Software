# Hardware Stores — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-HARD-001 | Bill 10×450 | Tenant type=hardware; user logged in | Execute bill 10×450 | Line total 4500 | P0 |
| TEST-HARD-002 | Unit conversion | Tenant type=hardware; user logged in | Execute unit conversion | Stock correct | P0 |
| TEST-HARD-003 | Credit sale | Tenant type=hardware; user logged in | Execute credit sale | Ledger | P0 |
| TEST-HARD-004 | Low stock alert | Tenant type=hardware; user logged in | Execute low stock alert | Notification | P0 |
| TEST-HARD-005 | Cross-tenant | Tenant type=hardware; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-HARD-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
