# Master Admin Manual — Business Billing

**Audience:** Prabha Technology operators  
**Product:** Business Billing  
**Provider:** Prabha Technology Pvt. Ltd.

Master Admin is a **platform operator**, not a business user. Master accounts live in `master_admins` (no `tenant_id`). They never share an Owner or Billing User dashboard.

---

## How to sign in

There is **no** “Master Login” item in the public navbar.

1. Open the public site (`/`).
2. Scroll to the footer.
3. Click the **small, low-contrast dot** at the bottom-right.
4. Sign in at `/master/login` with the Master Admin email and password.

The page heading is **Prabha Technology / Administration**. It has Email, Password, and Sign In only — no Register or Forgot Password.

If an Owner or Billing User tries this page, they see a generic **Invalid email or password** message and do not enter the Master console.

Unauthenticated visits to `/master/dashboard` (and other `/master/*` pages except login) redirect to `/master/login`.

Backend authorization still uses `POST /api/v1/auth/login` plus `master_required`. A stolen Owner JWT cannot call Master APIs.

### First Master account (ops)

After Phase 8 tables exist on the hosted DB, check readiness (read-only):

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\check_platform_ready.py
```

Exit `1` means the schema is in place but `master_admins` is empty. Then:

```powershell
cd backend
# set MASTER_ADMIN_EMAIL, MASTER_ADMIN_PASSWORD (min 8 chars), optional MASTER_ADMIN_NAME
.\.venv\Scripts\python.exe scripts\seed_master_admin.py
```

The script is idempotent. It will not overwrite an existing Master row. Do not commit real passwords. Run it with **`python.exe`**, not by double-clicking / invoking the `.py` path alone.

Expected success line: `Created master admin: <email>` (or `already exists`). Then confirm with `check_platform_ready.py` (`master_admin_seeded: true`).

---

## Console map

| Menu | Purpose |
|------|---------|
| Dashboard | Live counts. Each KPI opens a filtered list (see below). |
| Registration requests | Approve or reject public signups. Lists paginate (25 per page). |
| Trials | Businesses currently on a free trial (paginated, 25 per page) |
| Plans | Catalog price, features, public/active flags |
| Businesses | Assign plan, trial, renew, cancel, **activate / deactivate / suspend**. Filter by **Account** (login) or **Subscription**. Lists paginate (25 per page). |
| Audit log | Platform actions (Master only; no passwords/tokens). Paginated. |
| Trial settings | Default trial on/off, days, expiry-warning window |

### Dashboard KPI → list

| KPI | Opens |
|-----|--------|
| Total businesses | `/master/businesses` |
| Active businesses | `?tenant_status=ACTIVE` |
| Suspended businesses | `?tenant_status=SUSPENDED` (UI label: **Deactivated**) |
| Pending requests | Registration queue |
| Trial businesses | `/master/trials` |
| Expiring soon | `?status=EXPIRING` |
| Expired subscriptions | `?status=EXPIRED` |

Notification bell: unread expiry / business-lifecycle alerts. Opening a notice typically goes to **Businesses**.

---

## Registration approval

Public **Register Business** creates a `PENDING` request only. It does **not** create a tenant, owner login, or JWT. The queue paginates at 25 requests per page.

| Action | Result |
|--------|--------|
| **Approve** | Creates an ACTIVE tenant + verified OWNER. Starts a trial if trial is enabled. Owner can sign in at `/login`. |
| **Reject** | Requires a reason (≥ 8 characters). No tenant is created. The owner may submit again with the same email. |

Never approve from a screenshot alone: confirm business name, type, owner email, and mobile on the request detail. Password hashes are never shown.

---

## Business lifecycle (data is never deleted)

| Action | Tenant login | Billing | Data |
|--------|--------------|---------|------|
| **Activate** | Allowed | Follows subscription | Kept |
| **Deactivate** | Blocked | — | Kept (bills, items, users) |
| **Suspend** (billing) | Allowed | Locked (API 402) | Kept |
| **Resume** | Allowed | Restored if the period is still valid | Kept |
| **Cancel subscription** | Allowed | Locked | Kept |

Deactivate uses `tenants.status = SUSPENDED`. Suspend uses `subscriptions.status = SUSPENDED`. Do not confuse them.

The **Businesses** list has two filters:

- **Account** — `tenant_status=ACTIVE|SUSPENDED`. UI option **Deactivated** = `SUSPENDED` (login blocked).
- **Subscription** — `status=TRIAL|ACTIVE|EXPIRING|EXPIRED|CANCELLED|SUSPENDED|NONE` (billing entitlement).

Changing either filter updates the URL query string so dashboard deep-links work.

Manual **Renew** records an offline paid period. There is **no** in-app payment gateway. Changing a plan’s price later does **not** rewrite `price_at_purchase` on existing subscriptions.

Complimentary access (no end date) is used when you assign a plan without duration days, and for grandfathered tenants that already existed before subscriptions.

---

## Plans and landing prices

- Create / edit plans under **Plans**.
- **Public + Active** plans appear on the landing page via `GET /api/v1/public/plans`.
- Deactivating a plan hides it from the landing page. Existing billed businesses keep their snapshot price.
- Display order controls landing sequence.

---

## Trial settings

**Trial settings** apply to **newly approved** businesses only. Changing 15 → 30 days does not rewrite an existing trial’s end date.

If trial is **off**, approval creates the owner login but billing stays locked until you assign a plan or start a trial from **Businesses**.

---

## Expiry and notifications

- Warning window: `expiry_warning_days` (default 5).
- Owner: in-app `SUBSCRIPTION_EXPIRING` / `SUBSCRIPTION_EXPIRED` plus email when the job runs.
- Master: platform notification bell.
- Job: `POST /api/v1/master/jobs/expiry-check` or `python scripts/check_subscription_expiry.py` on a schedule.
- Notices are idempotent per subscription period (`subscription_notices`).

Expired or cancelled businesses can still sign in and use Profile. Catalog/billing APIs return **402** `SUBSCRIPTION_INACTIVE`.

---

## Platform audit

**Audit log** records Master actions: approve/reject, plan changes, trial settings, activate/deactivate/suspend, subscription updates.

It is **not** the same as Owner **Audit & Activity** (tenant `audit_logs`). Owner audit never includes Master operator actions as a substitute for this log.

---

## What Master must not do

- Do not run `backend/sql/02_schema.sql` against the hosted database (it drops tables).
- Do not delete tenant rows, bills, or users to “turn off” a business — deactivate or suspend instead.
- Do not put Master credentials in the public navbar or marketing copy.

## Support

- Email: prabha.technology.01@gmail.com  
- Phone: 8767865572  

Related: [registration-approval-flow.md](./registration-approval-flow.md) · [subscription-management.md](./subscription-management.md) · [plan-management.md](./plan-management.md) · [trial-management.md](./trial-management.md) · [backup-and-recovery.md](./backup-and-recovery.md)
