# Hardware / Building Material — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-BLDM-001 | Transfer stock | Tenant type=building_material; user logged in | Execute transfer stock | Balances move | P0 |
| TEST-BLDM-002 | Quotation → bill | Tenant type=building_material; user logged in | Execute quotation → bill | Linked | P0 |
| TEST-BLDM-003 | Challan print | Tenant type=building_material; user logged in | Execute challan print | OK | P0 |
| TEST-BLDM-004 | Transport fee on bill | Tenant type=building_material; user logged in | Execute transport fee on bill | Total correct | P0 |
| TEST-BLDM-005 | Cross-tenant warehouse | Tenant type=building_material; user logged in | Execute cross-tenant warehouse | 403/404 | P0 |

## Isolation

| TEST-BLDM-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
