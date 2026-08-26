# Industry Modules — Migration & Ops Runbook (BIZ-67)

**Audience:** Ops / Master Admin operators  
**Product:** Business Billing  
**Current Alembic head:** `20260826_biz66_perf_indexes`

This runbook is the **approved** path to enable industry schema on staging/production. It does not authorize new migrations by itself.

---

## Hard rules

1. **Never** run `backend/sql/02_schema.sql` on a database that already has live tenants (it drops tables).
2. **Always** take a verified backup + save a read-only schema inspect before upgrading.
3. Prefer **Alembic `flask db upgrade`** for industry packs on DBs that already have `alembic_version`.
4. Prefer **per–business-type enablement** (tenant `business_type`) — do not “turn on all industries” for every tenant at once.
5. No DROP/DELETE of production data without explicit written approval.
6. Platform/Master actions that flip tenant settings should remain visible in audit (`UPDATE_TENANT` / platform audit as applicable).

---

## Feature flags (how modules turn on)

Industry “flags” are **not** separate env toggles. They are:

| Layer | Mechanism |
|-------|-----------|
| Schema | Alembic revisions create tables/columns for all tenants |
| Runtime | `tenant.business_type` → `ModuleService` defaults (`backend/app/constants/modules.py`) |
| API | `@module_required(...)` + permissions |
| UI | Nav gated by enabled modules |

**Rollout pattern (safe):**

1. Upgrade schema on staging → dry-run (below).
2. Upgrade schema on production (backup first).
3. Enable **one** business type on a pilot tenant (Owner Settings / Master tooling).
4. Smoke that industry’s POS/board flows.
5. Repeat per business type. Avoid flipping every tenant to a new type in one batch.

Changing `business_type` is audited; treat it as a privileged ops action.

---

## Ordered Alembic chain

Single linear head. Print anytime:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\print_alembic_chain.py
```

Canonical order is also listed in [`11-alembic-revision-order.md`](./11-alembic-revision-order.md) (56 revisions, head = BIZ-66).

| Band | Revisions (examples) | Purpose |
|------|----------------------|---------|
| Foundation | `20260326_*` … `20260818_phase8_saas` | Auth, catalog, Phase 8 SaaS |
| Common platform | `20260820_biz01` … `20260822_biz09` | Business types, customers, purchases, ledger |
| F&B | `biz11` … `biz18` | Menu, tables, orders, KOT, recipes, cafe, wastage |
| Grocery / retail | `biz21` … `biz27` | Tiers, batches, variants, images, returns |
| Mobile / electronics | `biz29` … `biz33` | Serial, warranty, repairs, brand, install |
| Hardware / building | `biz35` … `biz38` | UoM, quotes, challans, transport, warehouses |
| Bakery / custom | `biz40`, `biz42` | Production, cake/custom orders |
| Books / furniture / wholesale / travel | `biz45` … `biz59` | Metadata, delivery, price lists, SO/PO, travel |
| Perf | `biz66_perf_indexes` | Tenant-leading composites |

Gate sprints without migrations (e.g. BIZ-34, 39, 43, 46, 50, 55, 60–65) do not appear in Alembic.

---

## Staging dry-run checklist

Copy this into the change ticket:

| Step | Action | Owner | Done |
|------|--------|-------|------|
| 1 | Backup staging DB; record location + timestamp | Ops | ☐ |
| 2 | `python scripts/inspect_database_schema.py --json-out staging-pre.json` | Ops | ☐ |
| 3 | Note current `SELECT version_num FROM alembic_version` | Ops | ☐ |
| 4 | `flask --app run:app db upgrade` (venv active, correct `DATABASE_URL`) | Ops | ☐ |
| 5 | Re-inspect → `staging-post.json`; diff table count | Ops | ☐ |
| 6 | Confirm head = `20260826_biz66_perf_indexes` | Ops | ☐ |
| 7 | Pilot tenant: switch business type → smoke POS/board for that industry | QA | ☐ |
| 8 | Confirm billing still works (create bill, stock movement) | QA | ☐ |
| 9 | Confirm audit row for tenant type change | QA | ☐ |

**CI / repo dry-run (no live DB):**

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_biz67_migration_ops_runbook.py -q
.\.venv\Scripts\python.exe scripts\print_alembic_chain.py
```

---

## Production upgrade path (industry-aware)

### A) DB already on Alembic (preferred after Phase 8 stamp)

```powershell
cd backend
# 1) Backup + inspect (mandatory)
.\.venv\Scripts\python.exe scripts\inspect_database_schema.py --json-out prod-pre.json

# 2) Upgrade
.\.venv\Scripts\Activate.ps1
$env:FLASK_ENV = "production"   # or development with prod URL — match your ops standard
flask --app run:app db upgrade

# 3) Verify
flask --app run:app db current
.\.venv\Scripts\python.exe scripts\print_alembic_chain.py
.\.venv\Scripts\python.exe scripts\inspect_database_schema.py --json-out prod-post.json
```

### B) Legacy DB upgraded only via `apply_pending_schema.py` (Phase 8 era)

1. Keep using helpers for **legacy** Phase 8 gaps if still needed:  
   `python scripts/apply_pending_schema.py`
2. Stamp Phase 8 **only if still on that head**:  
   `python scripts/stamp_alembic_head.py` → `20260818_phase8_saas`
3. Then run **`flask db upgrade`** through industry revisions to head.
4. If schema was applied out-of-band but matches head, align version with:  
   `python scripts/stamp_alembic_industry_head.py`  
   (refuses if representative industry tables are missing)

### C) Fresh empty local DB only

`sql/01_create_database.sql` + `sql/02_schema.sql` (or `sql/apply_schema.py`), then stamp/upgrade as needed. **Never** on live data.

---

## Rollback

| Situation | Action |
|-----------|--------|
| `db upgrade` fails mid-way | Restore from the backup taken before upgrade. Do not hand-edit half-migrated tables. |
| Upgrade succeeded but app regresses | Restore DB backup; redeploy previous app build. Investigate on staging clone. |
| Wrong database targeted | Restore that instance; fix `DATABASE_URL` / MYSQL_* before retry. |
| Need to undo a single revision | Prefer restore. Alembic `downgrade` is **not** the default prod path for industry packs (many revisions are additive CREATE-only; downgrades may be incomplete). |

There is **no** supported “reset production” script.

---

## Perf indexes ops note

BIZ-66 indexes ship in Alembic head. Optional catch-up on hosts that only run SQL helpers:

```powershell
.\.venv\Scripts\python.exe scripts\apply_perf_indexes.py
```

---

## Record template (each production change)

| Field | Value |
|-------|--------|
| Backup location | |
| Backup timestamp (UTC) | |
| Pre/post inspect JSON | |
| `alembic_version` before → after | |
| Pilot tenant + business_type | |
| Operator | |
| Sign-off | |

---

## Related

- [`09-migration-strategy.md`](./09-migration-strategy.md)
- [`11-alembic-revision-order.md`](./11-alembic-revision-order.md)
- [`07-indexes-and-performance.md`](./07-indexes-and-performance.md)
- Archive backup notes: [`../archive/flat-root/backup-and-recovery.md`](../archive/flat-root/backup-and-recovery.md)
- Sprint: [`../14-sprints/sprint-biz-67-industry-modules-migration-and-ops-runbook.md`](../14-sprints/sprint-biz-67-industry-modules-migration-and-ops-runbook.md)
