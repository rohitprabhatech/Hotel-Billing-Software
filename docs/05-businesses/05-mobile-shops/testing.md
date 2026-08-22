# Mobile Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-MOBL-001 | Register IMEI | Tenant type=mobile; user logged in | Execute register imei | Unique per tenant | P0 |
| TEST-MOBL-002 | Duplicate IMEI rejected | Tenant type=mobile; user logged in | Execute duplicate imei rejected | Validation | P0 |
| TEST-MOBL-003 | Sell IMEI | Tenant type=mobile; user logged in | Execute sell imei | Status Sold | P0 |
| TEST-MOBL-004 | Cannot resell same IMEI | Tenant type=mobile; user logged in | Execute cannot resell same imei | Blocked | P0 |
| TEST-MOBL-005 | Warranty created | Tenant type=mobile; user logged in | Execute warranty created | Dates correct | P0 |
| TEST-MOBL-006 | Repair ticket | Tenant type=mobile; user logged in | Execute repair ticket | Lifecycle | P0 |
| TEST-MOBL-007 | Cross-tenant IMEI | Tenant type=mobile; user logged in | Execute cross-tenant imei | 403/404 | P0 |

## Isolation

| TEST-MOBL-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
