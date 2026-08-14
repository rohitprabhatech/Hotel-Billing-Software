# Sprint Plan — P3-3 WhatsApp Bill Sharing / Delivery

**Date:** 2026-08-14  
**Mode:** Completed  
**Product:** Business Billing (existing multi-tenant SaaS)  
**Sprint ID:** **P3-3**

---

## 1. Audit summary (current architecture)

### What already works (must not break)

| Area | Current state |
|------|----------------|
| Bill create | `POST /api/v1/bills` — items, discount, `reference`/`table_number`, `payment_method` |
| Totals | Server-side only; line snapshots on `bill_items` |
| Print | Browser HTML thermal receipt (`PrintBillPage` → `window.print()`); `POST /bills/:id/print` increments `printed_count` + audit `PRINT_BILL` / `REPRINT_BILL` |
| Cancel | `POST /bills/:id/cancel` — financial status only |
| Sub-action pattern | Tenant from JWT; bill loaded by `id` + `tenant_id` |
| PDF tooling | `reportlab` already used for **report** export — **not** for bills |
| Settings | Owner `SettingsPage` → `PUT /tenants/me` typed tenant columns |
| Secrets today | **Global env only** (SMTP, JWT). No per-tenant encrypted API-key storage |
| Audit | `CREATE_BILL`, `CANCEL_BILL`, `PRINT_BILL`, `REPRINT_BILL` |

### Gaps vs this feature

| Need | Status |
|------|--------|
| Customer mobile / name on bill | **Missing** |
| Bill PDF for WhatsApp document | **Missing** (HTML print only) |
| WhatsApp Cloud API client | **Missing** |
| Per-tenant WhatsApp credentials | **Missing** |
| Delivery tracking table | **Missing** (`printed_count` only) |
| Success dialog WhatsApp button | **Missing** (Close + Print only) |
| Owner WhatsApp settings UI | **Missing** |

**Root conclusion:** Greenfield addition on top of existing bill APIs. Print stays as-is; WhatsApp is an independent delivery path that uses the **same saved bill row**.

---

## 2. Sprint goal

Enable Billing Users to **send an already-generated bill** to a customer via **official WhatsApp Cloud API**, with:

- Optional customer mobile on New Bill (not required for print-only)
- Owner per-tenant WhatsApp configuration (token never exposed to FE)
- Delivery attempts tracked separately from bill financial status
- Print unchanged and always available
- Retry delivery without creating a second bill

---

## 3. Explicit non-goals

- Unofficial WhatsApp Web / scraping / session hacks  
- Replacing or redesigning print receipts  
- Recalculating bill totals for WhatsApp  
- Global WhatsApp credentials shared across tenants  
- Payment gateway / SMS / email bill delivery  
- Live Meta template approval (document Owner steps; app stores template name)  
- Rebuilding billing UI or product  

---

## 4. Proposed architecture

```text
New Bill (optional customer phone)
        ↓
POST /bills  →  FINALIZED bill (unchanged money logic)
        ↓
Success dialog: [ Print Bill ]  [ Send on WhatsApp ]
        ↓                         ↓
openBillPrint (existing)    POST /bills/:id/send-whatsapp
                                   ↓
                    validate tenant WA config + phone
                                   ↓
                    generate PDF from saved bill snapshots
                                   ↓
                    WhatsApp Cloud API (document + template)
                                   ↓
                    bill_deliveries row + audit (masked phone)
```

### 4.1 Customer contact on bill

Add optional columns on `bills`:

| Column | Type | Notes |
|--------|------|--------|
| `customer_name` | `VARCHAR(120) NULL` | Optional |
| `customer_phone_country_code` | `VARCHAR(8) NULL` | e.g. `91` (digits, no `+`) |
| `customer_phone_national` | `VARCHAR(20) NULL` | National digits only |
| `customer_phone_e164` | `VARCHAR(20) NULL` | Normalized `+[cc][national]` for API |

- Collected optionally on **New Bill**  
- If missing at send time → dialog to enter number (updates bill contact fields, **does not** recreate bill)  
- Validation: strip spaces; require country code; E.164 normalize; reject invalid lengths (lib/`phonenumbers` preferred over India-only hardcode)

### 4.2 WhatsApp config (tenant-scoped)

New table `tenant_whatsapp_configs` (1:1 per tenant):

| Column | Notes |
|--------|--------|
| `tenant_id` PK/FK | Isolation |
| `phone_number_id` | Meta Phone Number ID |
| `waba_id` | WhatsApp Business Account ID |
| `display_phone_e164` | Optional display |
| `access_token_encrypted` | **Fernet** (or equivalent) using server env `WHATSAPP_TOKEN_ENCRYPTION_KEY` |
| `template_name` | Approved Meta template name |
| `template_language` | e.g. `en` |
| `is_enabled` | Soft connect/disconnect |
| `connected_at` / timestamps | |

**API responses never include raw token** — only `has_token: true/false`, masked IDs, status.

Owner Settings → new section **WhatsApp Integration** (preferred over new nav item for this sprint):

- Status Connected / Not connected  
- Phone Number ID, WABA ID (mask after save where appropriate)  
- Access token: write-only input (never echoed)  
- Template name + language  
- Save / Test connection / Disconnect  

### 4.3 Bill PDF

New server helper (e.g. `BillPdfService`) using **saved** bill + line snapshots + tenant business fields (name, address, phone, GSTIN, etc.) — same figures as print/list.

- Reuse `reportlab` already in stack  
- Generated on send (or cached in memory for request); not a second calculation path  
- Used as WhatsApp **document** media upload

### 4.4 Delivery tracking

New table `bill_deliveries`:

| Column | Notes |
|--------|--------|
| `id`, `tenant_id`, `bill_id` | Scoped FKs |
| `delivery_method` | `WHATSAPP` (PRINT remains via existing `printed_count` + optional future) |
| `recipient_phone_e164` | Full for ops |
| `recipient_phone_masked` | e.g. `+91******3210` for UI/audit |
| `status` | `PENDING` / `SENT` / `FAILED` |
| `provider_message_id` | Meta wamid if returned |
| `error_message` | Safe user/ops message (no secrets) |
| `attempted_by` | user id |
| `sent_at`, `created_at` | |

Bill financial `status` **unchanged** by delivery.

Bill serialize adds summary fields, e.g.:

- `whatsapp_delivery_status`: `null | PENDING | SENT | FAILED` (latest WhatsApp attempt)  
- `customer_phone_masked` for lists  

### 4.5 Send API

`POST /api/v1/bills/<bill_id>/send-whatsapp`  
Roles: `OWNER`, `BILLING_USER`  
Body (optional): `{ "country_code", "phone", "customer_name" }`

Backend steps (strict order):

1. Auth + tenant from JWT (never trust body `tenant_id`)  
2. Load bill by id + tenant; reject wrong tenant / cancelled if product rule says so (recommend: allow send only `FINALIZED`)  
3. Resolve phone (body override or bill fields); validate/normalize  
4. Load tenant WhatsApp config; reject if missing/disabled → clear message for Billing User  
5. Insert `bill_deliveries` `PENDING`  
6. Build PDF from saved bill  
7. Call WhatsApp Cloud API (upload media + template/document send)  
8. Update delivery `SENT`/`FAILED`; audit `BILL_SENT_WHATSAPP` / `BILL_WHATSAPP_FAILED` with **masked** phone  
9. Return professional success/error JSON  

**Never creates a second bill.**

Also:

- `GET/PUT /api/v1/tenants/me/whatsapp` (Owner only) — get status/masked config; put credentials  
- `POST /api/v1/tenants/me/whatsapp/test` — Owner test connection (no bill)  
- `POST /api/v1/tenants/me/whatsapp/disconnect` — clear token / disable  

### 4.6 Frontend

| Surface | Change |
|---------|--------|
| New Bill | Optional Customer name + mobile (country + number); success dialog: **Print Bill** + **Send on WhatsApp** (independent) |
| Send UX | Loading “Sending…”; disable double-click; if no phone → enter dialog; if not configured → “WhatsApp not configured… contact Owner” |
| Failure | Message + **Retry** + **Print Bill** |
| Bills history / detail | Delivery chip (WhatsApp Sent / Failed / —) beside Prints |
| Owner Settings | WhatsApp Integration section |
| Icons | MUI / existing `@mui/icons-material` (e.g. WhatsApp if available in installed set, else `Chat` / `Share`) |

### 4.7 WhatsApp message strategy

- Support **approved template** (name + language stored per tenant)  
- Document variables concept: business name, bill number, amount  
- Attach bill PDF as document where Cloud API + template allow  
- Do **not** hardcode a free-form session message that violates Meta rules  
- Dev/test: allow mock provider behind `WHATSAPP_PROVIDER=mock|meta` so CI works without real Meta credentials  

---

## 5. Security

- Token encrypted at rest; decrypt only in backend send path  
- Never return token in API JSON; never log token  
- Never store token in React / localStorage  
- Tenant isolation on config + deliveries + bill lookup  
- Mask phones in audit `new_data` and list UIs  
- Rate-limit send endpoint reasonably (reuse existing limiter patterns if present)  

---

## 6. Database / ops

- Migration + `scripts/apply_whatsapp_bill_delivery.py`  
- Wire into `apply_pending_schema.py`  
- Update `sql/02_schema.sql`  
- Env: `WHATSAPP_TOKEN_ENCRYPTION_KEY`, optional `WHATSAPP_PROVIDER=mock|meta`, optional Meta API base URL  

---

## 7. Testing plan

| Suite | Coverage |
|-------|----------|
| Unit/API | Phone normalize; send uses existing bill; no duplicate bill; FAILED leaves bill FINALIZED |
| Isolation | Tenant A cannot read B config / use B token / see B deliveries |
| Security | GET config never includes plaintext token |
| Mock provider | Success + failure paths without live Meta |
| FE build | Success dialog + Settings section compile |
| Regression | Existing bill create / print / cancel / stock tests still green |

Update `docs/test-business-billing-guide.md` with Shree General Store WhatsApp checklist (mock + optional live).

---

## 8. Documentation (after implement)

Update only what is shipped:

- `docs/user-manual.md`, `owner-manual.md`, `billing-user-manual.md`  
- `docs/database-design.md`, `docs/api-documentation.md`  
- `docs/test-business-billing-guide.md`  
- Roadmap Phase 3 row for P3-3  
- Completion report `docs/phase3-p3-3-whatsapp-bill-delivery.md`  

---

## 9. Implementation task order

1. Schema: bill customer fields + `tenant_whatsapp_configs` + `bill_deliveries` + apply script  
2. Phone normalize util + bill create/update contact fields  
3. Bill PDF from saved snapshots  
4. WhatsApp config service/routes (Owner) + encryption  
5. Send-whatsapp service + mock/meta provider + delivery + audit  
6. FE: New Bill fields + success dialog + retry/enter-number  
7. FE: Settings WhatsApp section + bills history delivery chip  
8. Tests + docs + completion report → **STOP**  

---

## 10. Acceptance criteria

1. Print Bill still works exactly as today  
2. Send on WhatsApp never creates a second bill  
3. Totals in PDF match saved `grand_total`  
4. Tenant A credentials never used for Tenant B  
5. Access token never visible in FE or API responses  
6. Failed send → bill remains FINALIZED; Retry + Print available  
7. Owner can configure / test / disconnect WhatsApp  
8. Billing User sees clear messages for missing phone / not configured / provider error  
9. Audit records send/fail with masked phone  
10. Automated tests + FE build green  

---

## 11. Risks / known limits (honest)

| Risk | Mitigation |
|------|------------|
| Meta template approval outside app | Store template name; docs for Owner; mock provider for CI |
| Document+template combo depends on Meta product rules | Prefer documented Cloud API document template flow; fall back message+PDF upload pattern if needed during implement |
| No existing Fernet pattern | Introduce small crypto helper + env key; document rotate |
| Live E2E with real WhatsApp | Optional manual; automated uses mock |

---

## 12. Approval gate

**No code will be written until you approve this plan.**

Please confirm or adjust:

1. Sprint **P3-3** scope as above — OK?  
2. WhatsApp settings as a **section inside Owner → Settings** (vs separate page)?  
3. Mock WhatsApp provider for CI — OK?  
4. Optional customer name + phone on New Bill — OK?  
5. Any must-have change before implementation?

Reply **approve** (with any deltas) to start coding.
