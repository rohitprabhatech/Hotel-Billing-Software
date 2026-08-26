# Bakery / Sweet Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-BAKE-001 | Create batch | Tenant type=bakery_sweets; user logged in | Execute create batch | Stock increases | P0 |
| TEST-BAKE-002 | Custom order advance | Tenant type=bakery_sweets; user logged in | Execute custom order advance | Balance due | P0 |
| TEST-BAKE-003 | Complete delivery | Tenant type=bakery_sweets; user logged in | Execute complete delivery | Status + invoice | P0 |
| TEST-BAKE-004 | Wastage reduces stock | Tenant type=bakery_sweets; user logged in | Execute wastage reduces stock | Correct qty | P0 |
| TEST-BAKE-005 | Expiry on batch | Tenant type=bakery_sweets; user logged in | Execute expiry on batch | Listed | P0 |
| TEST-BAKE-006 | Cross-tenant | Tenant type=bakery_sweets; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-BAKE-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.

## Automated (Phase 07 gate — BIZ-43)

```bash
cd backend
python -m pytest tests/test_biz40_bakery_production.py tests/test_biz41_bakery_batch_expiry_wastage.py tests/test_biz42_custom_cake_orders.py tests/test_biz43_bakery_testing_gate.py -q
```

Sign-off: [`docs/14-sprints/biz-43-bakery-gate-report.md`](../../14-sprints/biz-43-bakery-gate-report.md).

Covers production BOM effects, batch-on-produce, FEFO sell/wastage, cake order advances + status pipeline, isolation, permissions, audit.
