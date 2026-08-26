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

## Phase 06 automated gate (BIZ-39)

```bash
cd backend
python -m pytest tests/test_biz35_length_weight_area_uom.py tests/test_biz36_quotation_delivery_challan.py tests/test_biz37_trade_credit_transport.py tests/test_biz38_warehouse_stock_foundation.py tests/test_biz39_hardware_building_material_testing_gate.py -q
```

Sign-off: [`docs/14-sprints/biz-39-hardware-building-material-gate-report.md`](../../14-sprints/biz-39-hardware-building-material-gate-report.md).
