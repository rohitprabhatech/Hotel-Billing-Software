# Tenant Architecture

## Model

```
Platform (SaaS operator)
  master_admins, subscription_plans, platform_audit_logs

Tenant (= one business customer on SaaS)
  tenant_id on all operational rows
    users, customers, items, bills, orders, ...
```

There is **no** `businesses` table and **no** `business_id` on data rows.

## Tenant isolation (PASS)

| Layer | Mechanism |
|-------|-----------|
| Auth | JWT includes `tenant_id`; `@auth_required` binds `RequestContext` |
| Service | `require_request_context()` → `ctx.tenant_id` |
| Repository | Every query: `.filter(Model.tenant_id == tenant_id)` |
| Create | Services set `tenant_id=ctx.tenant_id`; body tenant_id ignored |

**Not used:** DB row-level security, separate schema per tenant, ORM global filter

## Business type (configuration, not isolation)

`tenants.business_type` — one of 13 codes — controls **enabled modules** via `constants/modules.py`.

Changing business type in Settings:
- Shows/hides industry APIs (KOT, serial/IMEI, travel, etc.)
- Does **not** partition existing data
- All items/bills remain in the same tenant scope

Document this for support and QA when switching types on a test tenant.

## Master admin cross-tenant access

`master_admins` may list/manage `tenants` for SaaS operations. Tenant JWT cannot access master routes.

## Tests

```bash
pytest tests/test_tenant_isolation.py -q
pytest tests/test_p2_13_tenant_isolation_matrix.py -q
pytest tests/test_biz64_tenant_isolation_regression_suite.py -q
```

## Known gap

`GET /api/v1/item-images/files/<filename>` — public if UUID known. Listing/upload is tenant-scoped.

See [DATABASE-AUDIT-REPORT.md](./DATABASE-AUDIT-REPORT.md) §6–7.
