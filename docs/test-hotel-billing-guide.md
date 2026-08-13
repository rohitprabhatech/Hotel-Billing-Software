# Hotel Billing Software - Complete Testing Guide

**Document type:** Manual QA / UAT guide  
**Application:** Multi-tenant Hotel Billing SaaS (Flask + React)  
**Based on:** Actual codebase inspection (routes, services, schemas, frontend pages)  
**Last updated:** March 2026

---

## 1. Purpose

This guide provides a complete, step-by-step manual testing process for the Hotel Billing Software — from hotel registration through billing, printing, reports, audit, email, security, and tenant isolation.

It is intended for:

- Developers verifying local changes
- QA testers performing regression / UAT
- Hotel owners / stakeholders validating business workflows

Every test case includes **Expected Result** fields. Fill **Actual Result** and **Status** during execution.

---

## 2. Testing Scope

### In scope (implemented)

- Hotel self-registration and tenant creation
- Email verification, forgot/reset password, change password
- Owner and Billing User roles
- JWT authentication and role-based route/API protection
- Tenant isolation (`tenant_id` from JWT / authenticated user)
- Categories (Owner manage; Billing User view)
- Items (Owner **and** Billing User create/edit/soft-deactivate; search; bill selection)
- Owner Item Activity page + dashboard Item Activity widget (immutable audit)
- Billing cart → finalize bill → print / reprint → cancel
- Owner dashboard, sales reports, CSV/Excel/PDF export
- Audit logs and fraud-style alerts (read-only; no delete)
- Owner hotel settings and profile
- Responsive owner/billing layouts

### Out of scope / Not Implemented (do not invent)

| Feature | Status |
|---------|--------|
| Percentage discount on bills | **Not Implemented** — discount is fixed ₹ only |
| Edit / remove line items after bill is saved | **Not Implemented** — only cancel whole bill |
| Hard DELETE of bills, bill items, or audit logs via API/UI | **Not Implemented** |
| Separate “GST on/off” toggle at bill time | **Not Implemented** — GST comes from each item’s `gst_percentage` (use `0` to disable tax for an item) |
| Tenant switcher for users | **Not Implemented** (by design) |
| Refresh tokens | **Not Implemented** — access JWT only |
| Super-admin / platform admin role | **Not Implemented** — only `OWNER` and `BILLING_USER` |
| Automatic use of tenant `default_gst_percent` when creating items | **Partial / gap** — field exists on tenant model/API; Settings UI and item-create do not apply it automatically |

---

## 3. Application Overview

| Layer | Stack |
|-------|--------|
| Frontend | React + Vite + MUI — default `http://localhost:5173` |
| Backend | Flask REST API — default `http://localhost:5000/api/v1` |
| Database | MySQL (`hotel_billing`) |
| Auth | JWT (`Authorization: Bearer <token>`) with claims `tenant_id`, `role`, `tv` (token version) |
| Tenancy | One hotel = one `tenants` row; all business data scoped by `tenant_id` |

### High-level flow

```text
Register Hotel → Create Tenant + OWNER → Verify Email → Login
    → Owner: Categories / Items / Item Activity / Users / Settings / Reports / Audit
    → Billing User: New Bill / Items / Categories (view) / Bills / Print
    → Owner: Dashboard Item Activity / Exports / Audit review
```

---

## 4. User Roles

The application supports exactly two roles:

### 4.1 OWNER (Hotel Owner)

**Can access (UI):**

- `/owner/dashboard`, `/owner/categories`, `/owner/items`, `/owner/item-activity`
- `/owner/bills`, `/owner/reports`, `/owner/audit`, `/owner/users`, `/owner/settings`
- `/owner/profile`, `/owner/change-password`
- Also `/billing/*` and `/print/bills/:billId`

**Can do (API):**

- Manage billing users (`/users`)
- Create/update/deactivate categories and items
- View item activity / full audit logs
- Update hotel profile (`PUT /tenants/me`)
- Reports and exports
- Create / cancel / print bills

**Cannot:**

- Switch to another hotel’s tenant
- Hard-delete bills, items, or audit logs
- Create another OWNER via the users API (API creates `BILLING_USER` only)

### 4.2 BILLING_USER

**Can access (UI):**

- `/billing`, `/billing/new`, `/billing/bills`
- `/billing/items`, `/billing/categories` (categories are **view-only**)
- `/billing/profile`, `/billing/change-password`
- `/print/bills/:billId`

**Can do (API):**

- Create / update / soft-deactivate items (audited; soft-delete only)
- List categories (active for billing); create bills; cancel bills; print/reprint
- View own tenant summary (`GET /tenants/me` limited)
- Change own password / update profile

**Cannot (expect 403 or frontend redirect):**

- Owner dashboard, reports, audit logs, item-activity API list, user management, hotel settings update
- Create/update categories
- Hard-delete items or audit logs
- Access another tenant’s data
- Hide item activity from the Owner (all item ops write immutable audit rows)

---

## 5. Prerequisites

1. MySQL database `hotel_billing` created and schema applied (including SaaS auth columns/tables).
2. Backend dependencies installed in `backend/.venv`.
3. Backend running (`python run.py` or equivalent) on port **5000**.
4. Frontend running (`npm run dev`) on port **5173**.
5. `.env` configured (`DATABASE_URL`, `JWT_SECRET_KEY`, `SECRET_KEY`, `FRONTEND_URL`).
6. For email tests: SMTP configured **or** use development mode with:
   - `MAIL_SUPPRESS_SEND=true`
   - `ALLOW_DEV_AUTH_TOKENS=true` (API returns `verification_token` / `reset_token` for local testing)
7. Optional demo seed (`scripts/seed_demo_data.py`) for isolation smoke tests with Hotel A / Hotel B.

---

## 6. Test Environment

| Item | Value |
|------|--------|
| Frontend URL | `http://localhost:5173` |
| Backend URL | `http://localhost:5000` |
| API Base | `http://localhost:5000/api/v1` |
| Database | MySQL — `hotel_billing` |
| Browser | Google Chrome (latest) + one secondary browser optional |
| API testing tool | Postman / Insomnia / curl |
| Email testing | SMTP inbox **or** API `verification_token` / `reset_token` when `ALLOW_DEV_AUTH_TOKENS=true` |
| OS | Windows / macOS / Linux (local) |

> Use **local/staging only**. Do not run destructive or injection tests against production.

---

## 7. Test Data

### 7.1 Hotel 1 (Tenant A) — primary

| Field | Value |
|-------|--------|
| Hotel Name | Hotel Chul Mutton |
| Business Name | Hotel Chul Mutton & Family Restaurant |
| Owner Name | Rahul Patil |
| Owner Email | `owner.hotel1@example.com` |
| Owner Mobile | `9876543210` |
| Password | `Test@12345` |
| Address | Pune Satara Road |
| City | Pune |
| State | Maharashtra |
| Pincode | `412205` |
| GSTIN | `27ABCDE1234F1Z5` |
| FSSAI | `11520036000280` |

**Record after registration:**

| Field | Value |
|-------|--------|
| Tenant ID | ________________ |
| Owner User ID | ________________ |
| Registration Date | ________________ |

### 7.2 Hotel 2 (Tenant B) — isolation

| Field | Value |
|-------|--------|
| Hotel Name | Shivraj Family Restaurant |
| Business Name | Shivraj Food Restaurant |
| Owner Name | Amit Shinde |
| Owner Email | `owner.hotel2@example.com` |
| Owner Mobile | `9876543211` |
| Password | `Test@12345` |
| Address | Pune-Satara Highway |
| City | Pune |
| State | Maharashtra |
| Pincode | `411001` |
| GSTIN | `27XYZAB5678C1Z2` |
| FSSAI | `11520036000281` |

**Record after registration:**

| Field | Value |
|-------|--------|
| Tenant ID | ________________ |
| Owner User ID | ________________ |

### 7.3 Billing User (Hotel 1)

| Field | Value |
|-------|--------|
| Name | Counter One |
| Email | `billing.hotel1@example.com` |
| Password | `Billing@12345` |

### 7.4 Optional demo seed credentials (if seeded)

| Email | Password | Role | Tenant |
|-------|----------|------|--------|
| `owner@hotela.com` | `Owner@12345` | OWNER | Hotel A |
| `billing@hotela.com` | `Billing@12345` | BILLING_USER | Hotel A |
| `owner@hotelb.com` | `Owner@12345` | OWNER | Hotel B |

> These are **dummy/test** credentials only.

### 7.5 Categories (Hotel 1)

Create:

1. Veg  
2. Non-Veg  
3. Bar  
4. Cold Drinks  
5. Ice Cream  
6. Rice  
7. Roti  

### 7.6 Items (Hotel 1)

| Category | Item | Price (₹) | GST % |
|----------|------|----------:|------:|
| Non-Veg | Chicken Sadhi Thali | 420 | 2.5 |
| Non-Veg | Mutton Sadhi Thali | 480 | 2.5 |
| Veg | Wanga Masala | 240 | 2.5 |
| Veg | Dal Tadka | 260 | 2.5 |
| Veg | Solkadhi | 50 | 2.5 |
| Veg | Masala Papad | 70 | 2.5 |
| Rice | Jeera Rice Half | 220 | 2.5 |
| Veg | Dahi Wati | 60 | 2.5 |
| Roti | Tandoor Roti | 30 | 2.5 |
| Cold Drinks | Pepsi | 50 | 2.5 |
| Ice Cream | Vanilla Ice Cream | 80 | 2.5 |

> GST is **per item**. Set `gst_percentage` when creating each item in Owner → Items.

---

## 8. Complete Test Execution Flow (recommended order)

```text
1. Environment smoke (health)
2. Register Hotel 1 + email verify + login
3. Register Hotel 2 + verify + login (for isolation)
4. Owner profile + hotel settings
5. Categories + items
6. Create billing user
7. Billing workflow (bills, print, cancel)
8. Historical price test
9. Owner dashboard + reports + export
10. Audit logs
11. Password / forgot password / email
12. Tenant isolation + JWT forgery
13. Security + UI responsive
14. End-to-end checklist + summary
```

---

## 9. Smoke / Health

### TC-HLTH-001 - API health

**Purpose:** Confirm backend is reachable.

**Steps:**

1. Open `GET http://localhost:5000/api/v1/health`
2. Open `GET http://localhost:5000/api/v1/health/ready`

**Expected Result:**

- `/health` → **200**, service OK
- `/health/ready` → **200** if DB connected; **503** if DB unavailable

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 10. Registration Testing

### TC-REG-001 - Register Hotel 1

**Purpose:** Create tenant + owner via self-registration.

**Preconditions:** Frontend and backend running; email `owner.hotel1@example.com` not already registered.

**Steps:**

1. Open `http://localhost:5173/`
2. Click **Register Your Hotel** (or open `/register`)
3. Enter Hotel 1 data from §7.1
4. Owner email = `owner.hotel1@example.com`
5. Password / Confirm = `Test@12345`
6. Submit **Create Hotel Account**

**API equivalent:**

```http
POST /api/v1/auth/register-hotel
Content-Type: application/json

{
  "hotel_name": "Hotel Chul Mutton",
  "business_name": "Hotel Chul Mutton & Family Restaurant",
  "address": "Pune Satara Road",
  "city": "Pune",
  "state": "Maharashtra",
  "pincode": "412205",
  "mobile": "9876543210",
  "gst_number": "27ABCDE1234F1Z5",
  "fssai_number": "11520036000280",
  "owner_name": "Rahul Patil",
  "owner_email": "owner.hotel1@example.com",
  "password": "Test@12345",
  "confirm_password": "Test@12345"
}
```

**Expected Result:**

- HTTP **201**
- Message indicates verification required
- Response includes `tenant_id` (UUID)
- New row in `tenants` and `users` with same `tenant_id`, role `OWNER`
- `users.email_verified = 0` (false) until verification
- Verification email sent (or `verification_token` returned when `ALLOW_DEV_AUTH_TOKENS=true`)
- In local UI, may auto-navigate to `/verify-email?token=...` in development

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED  
**Record Tenant ID:** ________________

---

### TC-REG-002 - Register Hotel 2

**Purpose:** Second tenant for isolation tests.

**Steps:** Same as TC-REG-001 using Hotel 2 data (`owner.hotel2@example.com`).

**Expected Result:**

- **201**, distinct `tenant_id` from Hotel 1
- Owner associated only with Hotel 2 tenant

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-REG-003 - Duplicate owner email

**Steps:** Re-register with `owner.hotel1@example.com`.

**Expected Result:** **409** — account with this email already exists.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-REG-004 - Password mismatch

**Steps:** Register with `password` ≠ `confirm_password`.

**Expected Result:** Validation error (**400**); no tenant created.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-REG-005 - Weak password

**Steps:** Password shorter than 8 characters.

**Expected Result:** **400** validation error.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 11. Email Verification

### TC-VER-001 - Verify email (happy path)

**Preconditions:** TC-REG-001 completed; capture `verification_token` from API/dev response or email link (`/verify-email?token=...`).

**Steps:**

1. Open verification link or `POST /api/v1/auth/verify-email` with `{ "token": "<token>" }`
2. Attempt login with owner credentials

**Expected Result:**

- Verify → **200**, email verified
- `users.email_verified = 1`, `email_verified_at` set
- Login succeeds when `EMAIL_VERIFICATION_REQUIRED=true`

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-VER-002 - Reuse verification token

**Steps:** Submit the same token again.

**Expected Result:** Error — invalid or already used token (**400**).

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-VER-003 - Invalid token

**Steps:** `POST /auth/verify-email` with `{ "token": "not-a-real-token-value-xxx" }`.

**Expected Result:** **400** invalid token.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-VER-004 - Expired token

**Steps:** Create a verification token, set `expires_at` in the past in DB (or wait if short expiry in a special test config), then verify.

**Expected Result:** **400** token expired.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-VER-005 - Resend verification

**Steps:** `POST /api/v1/auth/resend-verification` with `{ "email": "owner.hotel1@example.com" }` before verifying (or after partial flow).

**Expected Result:**

- **200** with generic success message (no account enumeration)
- New token issued when account needs verification

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 12. Login / Logout Testing

| ID | Purpose | Input | Expected |
|----|---------|-------|----------|
| TC-AUTH-001 | Valid owner login | Hotel 1 verified email + `Test@12345` | **200**, JWT, user role `OWNER`, redirect `/owner/dashboard` |
| TC-AUTH-002 | Wrong password | Correct email + `WrongPass1` | **401** Invalid email or password |
| TC-AUTH-003 | Invalid email | `nobody@example.com` + any password | **401** |
| TC-AUTH-004 | Unverified email | Register new hotel, skip verify, login | **401** Email not verified… |
| TC-AUTH-005 | Empty email | `""` | **400** validation |
| TC-AUTH-006 | Empty password | email only | **400** validation |
| TC-AUTH-007 | Logout | Authenticated `POST /auth/logout` | **200**, audit `LOGOUT`; client clears token |

### TC-AUTH-001 - Valid owner login

**Steps:**

1. Open `/login`
2. Enter `owner.hotel1@example.com` / `Test@12345`
3. Click Login

**Expected Result:** Token stored; land on Owner Dashboard; audit `LOGIN` for tenant.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-AUTH-002 - Wrong password

**Steps:** Login with wrong password.

**Expected Result:** Error message; no token; stay on login.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-AUTH-003 - Invalid email

**Expected Result:** **401** / error toast; no session.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-AUTH-004 - Unverified email

**Expected Result:** Login blocked until verification.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-AUTH-005 / TC-AUTH-006 - Empty fields

**Expected Result:** Browser/API validation prevents login.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-AUTH-007 - Logout

**Steps:** Use profile menu → Logout.

**Expected Result:** Redirect `/login`; token cleared; protected routes require login again.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 13. Tenant Isolation Testing (CRITICAL)

**Setup:**

- Tenant A = Hotel Chul Mutton (verified)
- Tenant B = Shivraj Family Restaurant (verified)
- Create at least one category, item, and bill under each tenant

### TC-ISO-001 - UI isolation (Owner A)

**Steps:**

1. Login as Hotel 1 owner
2. Open Items, Bills, Users, Reports, Audit, Settings
3. Confirm only Hotel 1 data / hotel name appears

**Expected Result:** No Hotel 2 names, items, bills, or users visible.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ISO-002 - UI isolation (Owner B)

**Steps:** Login as Hotel 2 owner; repeat checks.

**Expected Result:** Only Hotel 2 data.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ISO-003 - Cross-tenant bill ID (API)

**Steps:**

1. As Hotel A, create a bill; note `bill_id`
2. Login as Hotel B; capture JWT
3. `GET /api/v1/bills/{hotel-A-bill-id}` with Hotel B token

**Expected Result:** **404** Not found (tenant-scoped; do not leak existence with full payload).

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ISO-004 - Cross-tenant category / item / user / audit

Repeat with Hotel A resource IDs while authenticated as Hotel B:

| Resource | Request | Expected |
|----------|---------|----------|
| Category | `GET /categories/{id}` | **404** |
| Item | `GET /items/{id}` | **404** |
| User | `GET /users/{id}` | **404** |
| Audit | `GET /audit-logs/{id}` | **404** |
| Reports | `GET /reports/daily-sales` | Only Tenant B totals |

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ISO-005 - Export isolation

**Steps:** As Hotel A export daily sales; as Hotel B export daily sales; compare files.

**Expected Result:** Each file contains only that tenant’s bills/totals.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 14. Tenant ID Trust Testing

### TC-TID-001 - Forged tenant_id in body

**Steps:**

1. Login as Hotel A
2. `POST /api/v1/users` (create billing user) including `"tenant_id": "<Hotel-B-UUID>"` in JSON body

**Expected Result:**

- Body `tenant_id` is **ignored** (schemas use `unknown = EXCLUDE`)
- User is created under **Hotel A** only
- Hotel B user list does not show the new user

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-TID-002 - Query / URL cannot select tenant

**Steps:** Call list endpoints with `?tenant_id=<Hotel-B>` while logged in as Hotel A.

**Expected Result:** Still returns Hotel A data only (query param not used for tenancy).

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-TID-003 - JWT tenant claim mismatch

**Steps:** If testing with a manually altered JWT `tenant_id` claim (different from DB user), call `GET /auth/me`.

**Expected Result:** **401** Tenant mismatch / invalid token.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 15. Owner Profile & Hotel Settings

### TC-PROF-001 - View / update profile

**UI:** `/owner/profile`  
**API:** `GET /profile`, `PUT /profile` with `{ "name": "Rahul Patil", "phone": "9876543210" }`

**Expected Result:** Name updates on user; phone updates tenant contact phone used on receipts.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-PROF-002 - Request email change

**API:** `POST /profile/request-email-change` `{ "new_email": "owner.hotel1.new@example.com" }`

**Expected Result:**

- Pending email set; verification email/token for **new** address
- Current email remains until verification
- After verify → email updated; audit `EMAIL_CHANGED`

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-SET-001 - Hotel settings update + receipt

**UI:** `/owner/settings`  
**API:** `PUT /tenants/me`

Update:

- Business name, address, phone, GSTIN, FSSAI as in §7.1 (optionally refine address to `Pune Satara Road, Khed-Shivapur`)

**Steps:** Save settings → create a new bill → open print page.

**Expected Result:** Receipt header shows updated `business_name`, address, phone, GSTIN, FSSAI from tenant (via bill payload `tenant`).

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 16. Password Change Testing

### TC-PWD-001 - Owner change password (success)

**UI:** `/owner/change-password`  
**API:** `POST /auth/change-password`

```json
{
  "current_password": "Test@12345",
  "new_password": "NewTest@12345",
  "confirm_password": "NewTest@12345"
}
```

**Expected Result:**

- **200**; audit `PASSWORD_CHANGED`
- `token_version` increments — previous JWT rejected (**401**)
- Old password fails login; new password works
- Password-changed email attempted (suppressed in local if configured)

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

> After this test, either keep using `NewTest@12345` or reset back via forgot-password for later sections.

| ID | Case | Expected |
|----|------|----------|
| TC-PWD-002 | Wrong current password | **400** Current password is incorrect |
| TC-PWD-003 | Confirm mismatch | **400** |
| TC-PWD-004 | New password < 8 chars | **400** |
| TC-PWD-005 | Empty fields | **400** |
| TC-PWD-006 | Same old/new password | **400** must be different |
| TC-PWD-007 | Billing user self change | Same rules on `/billing/change-password` |
| TC-PWD-008 | Owner admin reset billing user | UI Users → Reset Password → `PATCH /users/{id}/password` |

---

## 17. Forgot / Reset Password

### TC-FP-001 - Happy path

**Steps:**

1. `/forgot-password` → enter owner email
2. Receive email **or** capture `reset_token` from API (dev)
3. Open `/reset-password?token=...` or `POST /auth/reset-password`
4. Set new password (≥ 8)
5. Login with new password

**Expected Result:** Single-use token; password updated; audit `PASSWORD_RESET_REQUESTED` then `PASSWORD_CHANGED`.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

| ID | Case | Expected |
|----|------|----------|
| TC-FP-002 | Unknown email | **200** generic message (no enumeration) |
| TC-FP-003 | Invalid token | **400** |
| TC-FP-004 | Reused token | **400** already used |
| TC-FP-005 | Expired token (`expires_at` past) | **400** expired |
| TC-FP-006 | Multiple forgot requests | Latest valid token works; older may still work until used/expired — document observed behavior |

---

## 18. Email Integration Testing

| Email | Trigger | Check |
|-------|---------|-------|
| Verify account | Register / resend / email change | Recipient, subject, link to `/verify-email?token=` |
| Reset password | Forgot password | Link to `/reset-password?token=`, ~1 hour expiry |
| Password changed | Change/reset password | Confirmation content |
| Login notification | Login when `SEND_LOGIN_NOTIFICATIONS=true` | Optional — **off by default** |

**Config checklist:**

- [ ] `MAIL_*` in `.env` (never commit real secrets)
- [ ] `MAIL_SUPPRESS_SEND` understood for local
- [ ] `FRONTEND_URL` correct for links
- [ ] Token not returned in production (`ALLOW_DEV_AUTH_TOKENS=false`)

---

## 19. Category Testing

**UI:** `/owner/categories`  
**APIs:** `POST/GET/PUT /categories`, `PATCH /categories/{id}/status`

### TC-CAT-001 - Create categories

Create the 7 categories from §7.5.

**Expected Result:** Each created under Hotel 1 `tenant_id`; audit `CREATE_CATEGORY`.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

| ID | Case | Expected |
|----|------|----------|
| TC-CAT-002 | Edit name/description | Updates; audit `UPDATE_CATEGORY` |
| TC-CAT-003 | Duplicate name under same parent | Conflict / validation per service rules |
| TC-CAT-004 | Empty name | **400** |
| TC-CAT-005 | Deactivate | `PATCH .../status` `{ "is_active": false }` → audit `DEACTIVATE_CATEGORY` |
| TC-CAT-006 | Reactivate | `{ "is_active": true }` |
| TC-CAT-007 | Billing user create category | **403** |
| TC-CAT-008 | Billing user list | Sees **active** categories only |

---

## 20. Item Testing

**UI:** `/owner/items`, `/billing/items`  
**APIs:** `POST/GET/PUT /items`, `PATCH /items/{id}/status` (OWNER + BILLING_USER)  
**Hard delete:** `DELETE /items/{id}` → **403** (not allowed)

Audit actions (immutable): `ITEM_CREATED`, `ITEM_UPDATED`, `ITEM_DEACTIVATED`, `ITEM_REACTIVATED` (+ `UPDATE_PRICE` / `CHANGE_GST` for price/GST detail).

### TC-ITM-001 - Create menu items (Owner)

Create all items in §7.6 with GST **2.5**.

**Expected Result:** Items linked to correct category + tenant; prices stored as decimals; audit `ITEM_CREATED`.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

| ID | Case | Expected |
|----|------|----------|
| TC-ITM-002 | Update price | `ITEM_UPDATED` + `UPDATE_PRICE` |
| TC-ITM-003 | Update GST % | `ITEM_UPDATED` + `CHANGE_GST` |
| TC-ITM-004 | Deactivate item | Soft `is_active=false`; excluded from `GET /items?is_active=true`; bill create rejects inactive |
| TC-ITM-005 | Negative / invalid price | **400** |
| TC-ITM-006 | Billing user create item | **201** + Owner sees `ITEM_CREATED` in Item Activity |

---

## 20A. Billing User Item Management & Owner Visibility

**Business rule:** Billing Users can manage items, but they cannot hide their actions from the Hotel Owner.

**Owner UI:** `/owner/item-activity` and Dashboard → Item Activity  
**API:** `GET /audit-logs?entity_type=ITEM` (OWNER only)

### TC-ITEM-001 - Billing User creates an item

**Purpose:** Item available for billing; Owner sees create activity.

**Preconditions:** Owner created category Non-Veg; Billing User logged in.

**Steps:**

1. Open `/billing/items` → Add Item  
2. Name `Chicken Biryani`, Category Non-Veg, Price `250`, GST `2.5`  
3. Save  
4. Owner opens `/owner/item-activity` (or Dashboard Item Activity)

**Expected Result:**

- Item created (**201**); appears in new bill search (`is_active=true`)
- Audit `ITEM_CREATED` with user = Billing User, new_values include price/GST/category
- Owner can see who/when/what

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-002 - Billing User edits an item

**Steps:** Change Chicken Biryani price 250 → 280.

**Expected Result:** Owner sees `ITEM_UPDATED` (and `UPDATE_PRICE`) with old ₹250 and new ₹280.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-003 - Billing User deactivates an item

**Steps:** Deactivate with reason `Item temporarily unavailable`.

**Expected Result:**

- `ITEM_DEACTIVATED` audit with reason  
- Item not selectable on `/billing/new`  
- Still listed on Items management (inactive) and Owner activity history

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-004 - Billing User attempts permanent delete

**Steps:** `DELETE /api/v1/items/{id}` as Billing User (or Owner).

**Expected Result:** **403** — permanent deletion not allowed; deactivate instead.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-005 - Create → bill → deactivate

**Steps:**

1. Billing User creates Item A  
2. Create bill using Item A  
3. Deactivate Item A  

**Expected Result:**

- Historical bill still shows Item A name/price snapshot  
- Item activity history still shows CREATE + DEACTIVATE  
- New bills cannot use Item A

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-006 - Billing User attempts to delete audit history

**Steps:** `DELETE /api/v1/audit-logs/{id}` as Billing User; also `GET /audit-logs` as Billing User.

**Expected Result:** Delete **404/405**; list **403**. History immutable.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-007 - Cross-tenant item activity

**Steps:** Hotel B owner requests Hotel A audit log id / Hotel A item id.

**Expected Result:** **404** / no data leakage.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-008 - Owner reactivates an item

**Steps:** Owner toggles inactive item back to active.

**Expected Result:** `ITEM_REACTIVATED` audit; item returns to billing search.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-009 - Item price change does not alter old bills

**Steps:** Bill at ₹250 → change item to ₹300 → new bill → reopen first bill.

**Expected Result:** Old bill line still ₹250; new bill ₹300 (`bill_items` snapshots).

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-ITEM-010 - Owner filters activity by Billing User

**Steps:** `/owner/item-activity` → Filter User = Billing User → Apply.

**Expected Result:** Only that user’s item actions listed.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 21. Billing User Management

### TC-USR-001 - Create billing user

**UI:** `/owner/users` → Add Billing User  
**API:** `POST /users` `{ "name", "email", "password" }`

**Expected Result:** **201**, role `BILLING_USER`, same `tenant_id`, `email_verified=true` (owner-created), audit `CREATE_USER`.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-USR-002 - Billing user login + role home

**Expected Result:** Redirect to `/billing` (not owner console).

### TC-USR-003 - Billing user blocked from owner APIs

Try `GET /reports/summary`, `GET /audit-logs`, `GET /users`, `PUT /tenants/me`.

**Expected Result:** **403**.

### TC-USR-004 - Deactivate billing user

**Expected Result:** User cannot login; owner cannot deactivate self.

---

## 22. Billing Workflow Testing

**UI:** `/billing/new`  
**API:** `POST /bills`

```json
{
  "items": [{ "item_id": "<uuid>", "quantity": 1 }],
  "discount": 0,
  "table_number": "T1"
}
```

### Important calculation rules (actual)

- Discount = **fixed rupees** only (not %)
- GST from each item’s `gst_percentage`
- CGST = SGST = half of item GST rate on taxable amount after proportional discount
- Grand total rounded to **whole rupee**; `round_off` stored
- Quantity must be **> 0** (up to 3 decimal places supported)
- Duplicate `item_id`s in one request are **merged**
- After save, bill status = `FINALIZED` — line items cannot be edited

### TC-BILL-001 - Test Bill 1 (full thali order)

**Cart:**

| Item | Qty | Line |
|------|----:|-----:|
| Chicken Sadhi Thali | 1 | 420 |
| Mutton Sadhi Thali | 1 | 480 |
| Wanga Masala | 1 | 240 |
| Dal Tadka | 1 | 260 |
| Solkadhi | 1 | 50 |
| Masala Papad | 2 | 140 |
| Jeera Rice Half | 1 | 220 |
| Dahi Wati | 1 | 60 |
| Tandoor Roti | 3 | 90 |

**Subtotal (verify):** ₹**1,960.00**

With **all lines GST 2.5%** and **discount ₹0**:

| Field | Expected |
|-------|----------|
| Subtotal | 1960.00 |
| Discount | 0.00 |
| Taxable | 1960.00 |
| CGST (1.25%) | 24.50 |
| SGST (1.25%) | 24.50 |
| GST total | 49.00 |
| Pre-round | 2009.00 |
| Round off | 0.00 |
| Grand total | **2009.00** |

> If any item GST differs, recalculate from backend response — do not force these numbers.

**Expected Result:** Bill **201**; UI totals match API; DB `bills` + `bill_items` rows; audit `CREATE_BILL`.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED  
**Bill Number:** ________________  
**Bill ID:** ________________

---

### TC-BILL-002 - Remove accidental cart item before save

**Steps:**

1. Add Chicken Thali, Mutton Thali, Pepsi, Vanilla Ice Cream
2. Remove Ice Cream in cart UI
3. Finalize bill

**Expected Result:** Finalized bill and DB `bill_items` do **not** include Ice Cream.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-BILL-003 - Quantity validation

| Qty | Expected |
|-----|----------|
| 1 | OK |
| 2 | Line amount ×2 |
| 10 | OK |
| 0 | Rejected (UI removes line / API **400**) |
| Negative | **400** |
| Decimal e.g. `1.5` | Accepted if > 0 (3 dp) |

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-BILL-004 - Discount validation (fixed ₹)

| Discount | Expected |
|----------|----------|
| 0 | OK |
| 50 | Taxable reduced; GST on reduced taxable |
| Equal to subtotal | Taxable 0; grand total 0 (after round rules) |
| Greater than subtotal | **400** |
| Negative | **400** |
| Percentage discount | **Not Implemented** |

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-BILL-005 - GST variants

| Case | How | Expected |
|------|-----|----------|
| GST 2.5% items | As §7.6 | CGST=SGST half-rate |
| GST 5% item | Create item gst 5 | Half = 2.5% each |
| GST 0% item | Item gst 0 | No tax on that line |
| Mixed GST in one bill | Different item rates | Line-level calc; bill totals sum |

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-BILL-006 - Clear cart

**Steps:** Add items → clear cart (if UI provides) → ensure no accidental POST.

**Expected Result:** No bill created until Generate/Save with items.

---

## 23. Bill Database Verification

After TC-BILL-001, inspect DB (DBeaver / SQL):

### `bills`

Check: `id`, `tenant_id` (= Hotel 1), `bill_number`, `bill_sequence`, `subtotal`, `discount`, `taxable_amount`, `cgst_amount`, `sgst_amount`, `gst_amount`, `round_off`, `grand_total`, `status`=`FINALIZED`, `created_by`, `created_at`, `printed_count`.

### `bill_items`

Check: `tenant_id`, `bill_id`, `item_id`, **`item_name` snapshot**, `quantity`, `unit_price`, `gst_percentage`, amounts.

### `audit_logs`

Check: `action`=`CREATE_BILL`, matching `tenant_id`, `entity_id`=bill id, user fields, timestamp.

**Status:** PASS / FAIL / BLOCKED

---

## 24. Historical Price Test

### TC-HIST-001 - Price change must not alter old bills

**Steps:**

1. Create item **Chicken Biryani** @ ₹250, GST 2.5
2. Create **Bill A** with 1× Chicken Biryani
3. Update item price to ₹300
4. Create **Bill B** with 1× Chicken Biryani
5. Re-open Bill A and Bill B (UI + `GET /bills/{id}`)

**Expected Result:**

- Bill A line `unit_price` / totals still based on **250**
- Bill B based on **300**
- Catalog item shows 300

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 25. Bill Printing & Reprint

**UI:** `/print/bills/:billId` (optional `?auto=1`)  
**API:** `POST /bills/{id}/print` (no body) — increments `printed_count`

### TC-PRT-001 - Print receipt content

Verify receipt shows:

- [ ] Hotel business name  
- [ ] Address / city / pincode / phone  
- [ ] GSTIN / FSSAI (when set)  
- [ ] Bill number, date/time  
- [ ] Items, qty, rate, amount  
- [ ] Subtotal, discount, CGST, SGST, grand total  
- [ ] “Thank You”  
- [ ] No owner dashboard chrome in print preview  
- [ ] Width toggle **58mm** / **80mm** (client-side CSS)

**Expected Result:** Printable thermal-style layout; print API audits `PRINT_BILL` on first print.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

### TC-PRT-002 - Reprint

**Steps:** Print once → open history → print again.

**Expected Result:**

- Same historical amounts
- **No new bill / no new sale**
- `printed_count` increments
- Audit `REPRINT_BILL` (not a second `CREATE_BILL`)

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 26. Bill Cancellation

### TC-CAN-001 - Cancel finalized bill

**API:** `POST /bills/{id}/cancel`  
```json
{ "reason": "Customer cancelled order" }
```

**Expected Result:**

- Status → `CANCELLED`
- Rows remain in `bills` / `bill_items`
- Cancel user + time + reason stored
- Audit `CANCEL_BILL`
- Sales totals for FINALIZED exclude this bill; cancelled count increases on dashboard

**Note:** Both OWNER and BILLING_USER may cancel (by design in current API).

| ID | Case | Expected |
|----|------|----------|
| TC-CAN-002 | Cancel already cancelled | **400** Only finalized bills can be cancelled |
| TC-CAN-003 | Empty reason | **400** |
| TC-CAN-004 | Cross-tenant cancel | **404** |

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 27. Delete / Fraud Resistance

### TC-DEL-001 - Attempt hard delete

Try via UI and API:

- `DELETE /api/v1/bills/{id}`
- `DELETE /api/v1/bill-items/{id}` (if guessed)
- `DELETE /api/v1/audit-logs/{id}`

**Expected Result:** **404** or **405** — no delete endpoints. Financial history retained; cancellation is the supported path.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 28. Audit Log Testing

**UI:** `/owner/audit`  
**API:** `GET /audit-logs`, `GET /audit-logs/alerts`, `GET /audit-logs/{id}` — **OWNER only**

Verify presence (as exercised) of actions:

| Action | Trigger |
|--------|---------|
| `REGISTER_HOTEL` | Registration |
| `EMAIL_VERIFIED` / `EMAIL_CHANGED` | Verify flows |
| `LOGIN` / `LOGOUT` | Auth |
| `PASSWORD_CHANGED` / `PASSWORD_RESET_REQUESTED` | Password flows |
| `CREATE_USER` / `UPDATE_USER` / `DEACTIVATE_USER` | Users |
| `UPDATE_PROFILE` / `EMAIL_CHANGE_REQUESTED` | Profile |
| `UPDATE_TENANT` | Settings |
| `CREATE_CATEGORY` / `UPDATE_CATEGORY` / `DEACTIVATE_CATEGORY` | Categories |
| `CREATE_ITEM` / `UPDATE_ITEM` / `UPDATE_PRICE` / `CHANGE_GST` / `DEACTIVATE_ITEM` | Items |
| `CREATE_BILL` / `CANCEL_BILL` / `PRINT_BILL` / `REPRINT_BILL` | Billing |
| `EXPORT_REPORT` | Report export |

Each log should include tenant, user (when applicable), entity type/id, timestamps, old/new data where applicable.

**Billing user access:** **403** / UI redirect.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 29. Owner Dashboard Testing

**UI:** `/owner/dashboard`  
**APIs:** `GET /reports/summary?period=...`, `GET /audit-logs/alerts`

### TC-DASH-001 - Metrics load

Period options: `today`, `yesterday`, `this_week`, `this_month`, `last_month`.

Verify cards:

- Sales (FINALIZED only)
- Bills count
- Discount
- GST
- Average bill
- Items sold
- Cancelled bills
- Day-wise chart
- Top items
- Non-info audit alerts (if any)

**Expected Result:** Figures match DB aggregates for the tenant and period.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

---

## 30. Sales Reports & Export

**UI:** `/owner/reports`  
**APIs:**

| Endpoint | Notes |
|----------|-------|
| `GET /reports/summary` | `period`, or custom `from`/`to` |
| `GET /reports/daily-sales` | optional `date` |
| `GET /reports/monthly-sales` | optional `year`, `month` |
| `GET /reports/custom-sales` | required `from`, `to` |
| `GET /reports/export` | `type=daily\|monthly\|custom`, `format=xlsx\|csv\|pdf` |

### TC-RPT-001 - Daily / monthly / custom

Create multiple bills; verify totals, GST, discounts, cancelled handling vs DB.

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-RPT-002 - Export CSV / Excel / PDF

**Expected Result:**

- File downloads and opens
- Data matches on-screen report
- Only current tenant
- Audit `EXPORT_REPORT`

**Actual Result:** ________________  
**Status:** PASS / FAIL / BLOCKED

### TC-RPT-003 - Billing user export

**Expected Result:** **403**.

---

## 31. Owner Bills History

**UI:** `/owner/bills` and `/billing/bills`  
**API:** `GET /bills`, `GET /bills/today-summary`, `GET /bills/{id}`

**Expected Result:** List scoped to tenant; detail includes items + tenant print info.

---

## 32. UI / Responsive Testing

Test at:

| Device | Resolution |
|--------|------------|
| Desktop | 1920×1080, 1366×768 |
| Tablet | 768×1024 |
| Mobile | 390×844 |

Check pages: `/`, `/login`, `/register`, owner drawer (collapses to hamburger on small screens), billing nav, new bill, reports tables, dialogs.

Look for: overflow, clipped text, unusable tables, console errors, broken network calls.

**Status:** PASS / FAIL / BLOCKED

---

## 33. Security Testing (local/staging only)

| ID | Test | Expected |
|----|------|----------|
| TC-SEC-001 | No JWT on protected API | **401** |
| TC-SEC-002 | Invalid JWT | **401** |
| TC-SEC-003 | Expired JWT | **401** |
| TC-SEC-004 | Wrong role (billing → reports) | **403** |
| TC-SEC-005 | Cross-tenant IDs | **404** |
| TC-SEC-006 | Forged body `tenant_id` | Ignored; data stays in caller tenant |
| TC-SEC-007 | After password change, old JWT | **401** (`tv` mismatch) |
| TC-SEC-008 | SQL injection in login email / item name | No DB error leak; rejected/safe |
| TC-SEC-009 | XSS in category/item name | Stored escaped / not executed in UI |
| TC-SEC-010 | Negative price / qty / discount | **400** |
| TC-SEC-011 | Invalid bill/item UUID formats | **400**/**404** |
| TC-SEC-012 | Rate limit login (many attempts) | Limited (20/min configured) |

**Do not** run destructive tests on production data.

---

## 34. Database Integrity Checks

Verify schema includes (among others):

- `tenants`, `users`, `roles`, `categories`, `items`
- `bills`, `bill_items`, `bill_number_counters`
- `audit_logs`
- `password_reset_tokens`, `email_verification_tokens`

Checks:

- [ ] FKs: `users.tenant_id` → `tenants.id`, etc.
- [ ] Unique `(tenant_id, email)` on users
- [ ] Bill numbers unique per tenant design
- [ ] Decimal money fields not float-drifted in app layer
- [ ] No orphan `bill_items` without bill
- [ ] Cross-tenant FK misuse prevented by service filters

---

## 35. API Testing Matrix (core)

Use Bearer token unless noted. Success codes as implemented.

| Method | Endpoint | Auth | Roles | Success | Key negatives |
|--------|----------|------|-------|---------|---------------|
| POST | `/auth/register-hotel` | No | — | 201 | 400, 409 |
| POST | `/auth/verify-email` | No | — | 200 | 400 used/expired |
| POST | `/auth/login` | No | — | 200 | 401 |
| POST | `/auth/logout` | Yes | any | 200 | 401 |
| GET | `/auth/me` | Yes | any | 200 | 401 |
| POST | `/auth/forgot-password` | No | — | 200 | 400 empty |
| POST | `/auth/reset-password` | No | — | 200 | 400 |
| POST | `/auth/change-password` | Yes | any | 200 | 400 |
| GET/PUT | `/profile` | Yes | any | 200 | 401 |
| POST | `/profile/request-email-change` | Yes | any | 200 | 400/409 |
| GET/POST | `/users` | Yes | OWNER | 200/201 | 403 billing |
| PATCH | `/users/{id}/password` | Yes | OWNER | 200 | 403/404 |
| GET/PUT | `/tenants/me` | Yes | GET both; PUT OWNER | 200 | 403 billing PUT |
| CRUD-ish | `/categories`, `/items` | Yes | writes OWNER | 201/200 | 403/404 |
| POST | `/bills` | Yes | OWNER, BILLING | 201 | 400 invalid cart |
| POST | `/bills/{id}/cancel` | Yes | both | 200 | 400/404 |
| POST | `/bills/{id}/print` | Yes | both | 200 | 404 |
| GET | `/reports/*` | Yes | OWNER | 200 | 403 |
| GET | `/reports/export` | Yes | OWNER | file | 400 bad format |
| GET | `/audit-logs*` | Yes | OWNER | 200 | 403 |
| DELETE | `/bills/{id}` | — | — | **N/A** | 404/405 |

### Example: POST `/bills`

**Authentication:** Required  
**Role:** `BILLING_USER` or `OWNER`  
**Expected success:** **201**

Negative cases: missing items, inactive item, wrong-tenant item id, qty ≤ 0, discount > subtotal, unauthorized.

---

## 36. Complete End-to-End Scenario

Execute in one session and tick:

1. [ ] Register Hotel 1  
2. [ ] Tenant UUID created  
3. [ ] Owner created  
4. [ ] Verify email  
5. [ ] Owner login  
6. [ ] Update profile  
7. [ ] Change password (then login again)  
8. [ ] Update hotel settings (GSTIN/FSSAI)  
9. [ ] Add categories  
10. [ ] Add food items (§7.6)  
11. [ ] Create billing user  
12. [ ] Billing user login  
13. [ ] Create bill (cart)  
14. [ ] Remove accidental item  
15. [ ] Change quantity  
16. [ ] Apply fixed discount  
17. [ ] Confirm GST / grand total  
18. [ ] Finalize / save bill  
19. [ ] Print bill (58mm and 80mm UI)  
20. [ ] Reprint bill  
21. [ ] Cancel a separate test bill with reason  
22. [ ] Owner checks audit log  
23. [ ] Owner checks today’s sales / dashboard  
24. [ ] Generate daily + monthly report  
25. [ ] Export xlsx/csv/pdf  
26. [ ] Verify DB rows  
27. [ ] Verify Hotel 2 cannot see Hotel 1 data  

**E2E Status:** PASS / FAIL / BLOCKED  
**Notes:** ________________

---

## 37. Test Result Template (copy per case)

```text
### TC-XXXX - Test Name

Purpose:
...

Preconditions:
...

Steps:
1.
2.
3.

Test Data:
...

Expected Result:
...

Actual Result:
...

Status:
PASS / FAIL / BLOCKED

Bug ID:
...

Notes:
...
```

---

## 38. Final Test Summary

| Module | Total Tests | Passed | Failed | Blocked | Status |
|--------|-------------|--------|--------|---------|--------|
| Registration | | | | | |
| Email verification | | | | | |
| Authentication | | | | | |
| Tenant isolation | | | | | |
| Tenant ID trust | | | | | |
| Profile / settings | | | | | |
| Password / forgot | | | | | |
| Email delivery | | | | | |
| Categories | | | | | |
| Items | | | | | |
| Billing item mgmt / Item Activity | | | | | |
| Billing users | | | | | |
| Billing / GST / discount | | | | | |
| Historical price | | | | | |
| Printing / reprint | | | | | |
| Cancellation | | | | | |
| Delete resistance | | | | | |
| Audit | | | | | |
| Dashboard | | | | | |
| Reports / export | | | | | |
| UI responsive | | | | | |
| Security | | | | | |
| Database | | | | | |
| **Overall** | | | | | |

---

## 39. Bug Report Template

```text
Bug ID:
Title:
Module:
Severity: Critical / High / Medium / Low
Priority: P1 / P2 / P3 / P4
Environment: Local / Staging  |  Browser:  |  API build:
User Role: OWNER / BILLING_USER
Tenant: Hotel Chul Mutton / Shivraj ...
Steps to Reproduce:
1.
2.
Expected Result:
Actual Result:
Screenshot:
API Request:
API Response:
Database Evidence:
Status: Open / Fixed / Verified / Won't Fix
```

---

## 40. Final QA Checklist

- [ ] Hotel registration works  
- [ ] Tenant is created with unique UUID `tenant_id`  
- [ ] Owner is created and linked to that tenant  
- [ ] Email verification works  
- [ ] Unverified login is blocked (when `EMAIL_VERIFICATION_REQUIRED=true`)  
- [ ] Owner login works  
- [ ] Billing User create + login works  
- [ ] Tenant isolation works (UI + API)  
- [ ] Forged `tenant_id` in body is ignored  
- [ ] Categories work  
- [ ] Items work (Owner + Billing User)  
- [ ] Billing User item create/edit/deactivate is audited  
- [ ] Owner Item Activity page / dashboard widget works  
- [ ] Hard delete item is blocked  
- [ ] Inactive items excluded from new bills but kept in history  
- [ ] Billing cart works  
- [ ] Remove cart item before save works  
- [ ] Quantity validation works  
- [ ] Fixed discount works; over-discount rejected  
- [ ] GST CGST/SGST match backend  
- [ ] Bill saved to `bills` + `bill_items`  
- [ ] Historical price snapshots preserved  
- [ ] Bill printing works (58/80mm UI)  
- [ ] Reprint works without new sale  
- [ ] Cancellation works with reason + audit  
- [ ] No hard-delete of bills/audit via API  
- [ ] Audit logs work for sensitive actions  
- [ ] Password change works and revokes old JWT  
- [ ] Forgot / reset password works  
- [ ] Email templates/links correct (or dev tokens)  
- [ ] Owner dashboard metrics correct  
- [ ] Daily / monthly / custom sales correct  
- [ ] Export xlsx/csv/pdf works and is tenant-scoped  
- [ ] UI responsive on desktop/tablet/mobile  
- [ ] Security tests pass on local/staging  
- [ ] Database integrity checks pass  
- [ ] No cross-tenant data leakage  
- [ ] No critical bugs remain  

---

## 41. Implementation Gaps (for testers)

Document these so failures are not mis-filed as regressions:

1. **Discount type:** fixed ₹ only — percentage discount UI/API **Not Implemented**.  
2. **Post-finalize line edit/remove:** **Not Implemented** — use cancel.  
3. **DELETE APIs** for bills/items/audit: **Not Implemented**.  
4. **Login notification emails:** only when `SEND_LOGIN_NOTIFICATIONS=true`.  
5. **Tenant `default_gst_percent`:** not auto-applied on item create / not on Settings form — set GST per item.  
6. **Billing users can cancel bills** — intentional in current API (not owner-only).  

---

## 42. Quick Frontend Route Map

| Route | Role |
|-------|------|
| `/`, `/login`, `/register`, `/forgot-password`, `/reset-password`, `/verify-email` | Public |
| `/owner/*` including `/owner/item-activity` | OWNER |
| `/billing/*` including `/billing/items`, `/billing/categories` | BILLING_USER or OWNER |
| `/print/bills/:billId` | BILLING_USER or OWNER |

---

**End of testing guide.**  
Execute tests in a clean local database when certifying a release; keep Hotel 1 and Hotel 2 credentials only in secure test notes, not in production.
