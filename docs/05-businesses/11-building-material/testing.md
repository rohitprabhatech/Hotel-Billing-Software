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

## Phase 06 automated gate (BIZ-39)

```bash
cd backend
python -m pytest tests/test_biz35_length_weight_area_uom.py tests/test_biz36_quotation_delivery_challan.py tests/test_biz37_trade_credit_transport.py tests/test_biz38_warehouse_stock_foundation.py tests/test_biz39_hardware_building_material_testing_gate.py -q
```

Sign-off: [`docs/14-sprints/biz-39-hardware-building-material-gate-report.md`](../../14-sprints/biz-39-hardware-building-material-gate-report.md).
