# Sprint 2 — Cloud Schema Diff + Safe Upgrade Plan

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Nature:** Read-only comparison and upgrade planning only  
**Product:** Business Billing · Prabha Technology Pvt. Ltd.

---

## Scope

Sprint 2 used the user-provided cloud database creation SQL as the deployment baseline and compared it against:

- current SQLAlchemy models
- current `backend/sql/02_schema.sql`
- current idempotent upgrade helper scripts

No migration was executed. No database or application code was changed.

---

## Baseline used

The provided cloud-create SQL for `u583892242_HotelBillingDB` contains these production-era tables:

- `tenants`
- `roles`
- `users`
- `password_reset_tokens`
- `email_verification_tokens`
- `categories`
- `items`
- `bill_number_counters`
- `bills`
- `bill_items`
- `notifications`
- `tenant_whatsapp_configs`
- `bill_deliveries`
- `audit_logs`
- `stock_movements`

This confirms the live database was originally created from a schema **before** the Phase 8 Master Admin / SaaS subscription tables were added.

---

## Exact schema diff vs current codebase

### Tables missing from the provided cloud SQL baseline

The current backend expects these tables, but they do **not** exist in the provided cloud-create SQL:

1. `master_admins`
2. `registration_requests`
3. `platform_settings`
4. `subscription_plans`
5. `subscriptions`
6. `subscription_notices`
7. `platform_notifications`

### Existing tables that already match current expectations closely

The provided cloud SQL already contains current-compatible versions of the main tenant/billing tables, including:

- `tenants.business_type`
- `users.token_version`
- `categories.parent_key`
- `items.created_by`, `sku`, `cost_price`, stock fields
- `bills.payment_method`, customer fields, finalized default
- `bill_items.item_id` with `ON DELETE SET NULL`
- `bill_deliveries` with WhatsApp / print / email states
- `notifications`
- `audit_logs`
- `stock_movements`

So the main gap is not old core billing structure; it is the **missing Phase 8 SaaS control-plane schema**.

---

## Model vs baseline conclusion

### Current backend models require

- separate platform operators: `master_admins`
- pending approval flow: `registration_requests`
- global trial/warning config: `platform_settings`
- public/private plan catalog: `subscription_plans`
- tenant entitlement rows: `subscriptions`
- idempotent expiry notices: `subscription_notices`
- platform-wide master alerts: `platform_notifications`

### Provided cloud SQL supports only

- multi-tenant billing app
- tenant auth
- billing/report/audit/inventory/WhatsApp delivery

It does **not yet** support the Master Admin SaaS management layer.

---

## Safe non-destructive upgrade path

For a database created from the provided SQL baseline, the current repository intends this upgrade order:

1. `apply_master_admins.py`
2. `apply_registration_requests.py`
3. `apply_trial_management.py`
4. `apply_subscription_plans.py`
5. `apply_subscription_lifecycle.py`
6. `apply_expiry_notifications.py`

This sequence is already wired into:

- `backend/scripts/apply_pending_schema.py`

### What each step adds

#### 1. `apply_master_admins.py`

Creates:

- `master_admins`

Purpose:

- separate platform login identity
- no `tenant_id`
- unique email
- independent `token_version`

#### 2. `apply_registration_requests.py`

Creates:

- `registration_requests`

Purpose:

- public business signup queue
- `PENDING` / `APPROVED` / `REJECTED`
- links to `master_admins`
- optional link to created `tenant`

#### 3. `apply_trial_management.py`

Creates:

- `platform_settings`
- `subscriptions`

Purpose:

- global trial / expiry-warning settings
- tenant entitlement table
- subscription statuses and lifecycle timestamps

#### 4. `apply_subscription_plans.py`

Creates:

- `subscription_plans`

Also wires:

- `subscriptions.plan_id` foreign key

Purpose:

- DB-driven plans
- public/private visibility
- trial eligibility
- price / billing cycle / display order
- seeds default `Business Billing Plan`

#### 5. `apply_subscription_lifecycle.py`

Does not create tables. It backfills data safely:

- gives one complimentary `ACTIVE` subscription to any tenant that has no subscription row

Purpose:

- prevents existing businesses from being locked out after enabling subscription enforcement

#### 6. `apply_expiry_notifications.py`

Creates:

- `subscription_notices`
- `platform_notifications`

Purpose:

- idempotent expiry alert log
- separate master-side notifications

---

## Operational safety notes

### Do not use the original create SQL again on the live DB

The provided SQL file contains:

- `DROP TABLE IF EXISTS ...`

So it must **never** be re-run against the existing production database.

### Do not use `backend/sql/02_schema.sql` on the live DB

Current `02_schema.sql` is a full greenfield schema and also contains destructive drops. It is only suitable for:

- empty database creation
- local/dev rebuilds

### Current safest intended path in this repo

For the baseline you shared, the repository’s intended production-safe path is:

```text
python scripts/apply_pending_schema.py
```

with a valid `DATABASE_URL` targeting the existing DB.

---

## Important unresolved verification gap

Even with the create SQL baseline, one thing is still unknown:

**whether the live cloud database already received some or all of those helper-script upgrades later.**

So Sprint 2 can now state:

- what the original deployed schema lacked
- what the current repo expects
- what the non-destructive upgrade order is

But Sprint 2 still cannot certify:

- current live table inventory
- current live foreign keys / indexes
- whether `master_admins`, `subscriptions`, etc. already exist today

That requires a real live DB inspection or schema export.

---

## Recommended pre-upgrade verification

Before any actual DB update on `u583892242_HotelBillingDB`, verify:

1. backup exists and restore path is tested
2. current live table list
3. current live `SHOW CREATE TABLE` for:
   - `master_admins`
   - `registration_requests`
   - `platform_settings`
   - `subscription_plans`
   - `subscriptions`
   - `subscription_notices`
   - `platform_notifications`
4. current row counts for:
   - `tenants`
   - `users`
   - `bills`
   - `bill_items`
   - `audit_logs`
5. whether `alembic_version` exists and, if yes, its value

---

## Decision recommendation

For the database baseline you provided, the repository is already prepared for a **non-destructive Phase 8 upgrade**, but only through the helper-script path, not through a complete Alembic chain.

Recommended decision for the next implementation sprint:

- treat the provided SQL file as the **original deployed baseline**
- use helper-script / `apply_pending_schema.py` logic as the immediate operational path
- verify actual live DB state before executing any write operation
- postpone Alembic normalization until after the live DB is inspected

---

## Changed files in Sprint 2

- `docs/sprint-2-cloud-schema-diff-and-upgrade-plan.md` — new schema diff and safe upgrade plan

---

## Acceptance status

| Criterion | Result |
|-----------|--------|
| Cloud-create SQL baseline analyzed | Yes |
| Current codebase schema diff identified | Yes |
| Exact missing Phase 8 tables listed | Yes |
| Safe non-destructive upgrade order defined | Yes |
| Live current cloud DB state certified | No — still needs inspection/export |

---

**Stopped.** Sprint 2 completed as a schema-diff and upgrade-planning sprint only.
