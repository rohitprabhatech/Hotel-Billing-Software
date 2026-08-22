# Travel Agencies — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-TRVL-001 | Create package | Tenant type=travel_agency; user logged in | Execute create package | Service catalog | P0 |
| TEST-TRVL-002 | Booking + advance | Tenant type=travel_agency; user logged in | Execute booking + advance | Balance due | P0 |
| TEST-TRVL-003 | Complete booking | Tenant type=travel_agency; user logged in | Execute complete booking | Status | P0 |
| TEST-TRVL-004 | Commission calc | Tenant type=travel_agency; user logged in | Execute commission calc | Correct | P0 |
| TEST-TRVL-005 | Service invoice | Tenant type=travel_agency; user logged in | Execute service invoice | No stock move | P0 |
| TEST-TRVL-006 | Cross-tenant booking | Tenant type=travel_agency; user logged in | Execute cross-tenant booking | 403/404 | P0 |

## Isolation

| TEST-TRVL-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
