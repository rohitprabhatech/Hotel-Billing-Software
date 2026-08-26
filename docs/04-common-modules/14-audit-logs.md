# Common Module — Audit Logs

Tenant `audit_logs` + platform `platform_audit_logs`. Item activity visible to Owner. No secrets in snapshots.

## Completeness checklist (BIZ-65)

| Area | Status |
|------|--------|
| Industry CREATE/UPDATE/status audited | Done (repairs, install, quotes, challans, custom orders, production, deliveries, SO/PO, price lists, travel, KOT) |
| DELETE leaves audit | Done (`DELETE_PRICE_LIST`, travel itinerary/document deletes) |
| `old_data` / `new_data` on updates | Done for warehouses, tour packages, travel agents, commission status |
| Default warehouse auto-create audited | Done (`CREATE_WAREHOUSE` + `auto_default`) |
| Secret / PII scrub | Done via `app.utils.audit_scrub` (passwords dropped; `document_number` → `[REDACTED]`) |
| Module filters | Done — `GET /audit-logs?module=` + `GET /audit-logs/meta` |
| AuditPage module / entity filters | Done |
| Industry permission matrix | `INDUSTRY_PERMISSION_MATRIX` in `permissions.py` |
| Owner-only audit access | Unchanged (role Owner) |

## API

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/v1/audit-logs` | Filters: `user_id`, `action`, `entity_type`, `entity_id`, `module`, `bill_number`, `q`, `from`, `to`, pagination |
| GET | `/api/v1/audit-logs/meta` | Modules, entity types, industry actions |
| GET | `/api/v1/audit-logs/alerts` | Soft activity indicators |
| GET | `/api/v1/audit-logs/{id}` | Full old/new payloads (scrubbed) |

There is **no delete** endpoint for audit rows.

## Permission matrix (industry → capability)

See `INDUSTRY_PERMISSION_MATRIX`. Verticals reuse coarse codes (`billing`, `items.*`, `kot.*`, `purchases.*`, `production.*`) plus `module_required`. Price lists / tour package **writes** are Owner-only (`items.write`).
