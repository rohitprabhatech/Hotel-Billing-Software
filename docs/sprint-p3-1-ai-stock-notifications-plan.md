# Sprint Plan — AI blank page + Stock enforcement + Notifications

**Date:** 2026-08-14  
**Mode:** Audit complete — **awaiting approval before implementation**  
**Product:** Business Billing (existing multi-tenant SaaS)

---

## 1. Root cause — AI blank page (`/owner/ai`)

**Cause:** `AiAssistantPage.jsx` renders `<Card>` / `<CardContent>` but does **not** import them from `@mui/material`.

- First paint (empty / filter bar) often works.
- After **Analyze** succeeds and insights/recommendations render → `ReferenceError: Card is not defined`.
- No React ErrorBoundary → entire app shell goes white (blank page).

**Not the cause:** AI API, tenant JWT, charts (none on this page), lazy route, auth redirect.

**Tenant security (already OK):** AI uses JWT → `RequestContext.tenant_id` only; no client `tenant_id`. Owner-only route.

---

## 2. Root cause — stock overselling

**Cause:** `items.stock_quantity` is **catalog metadata only**.  
`BillService.create_bill` never reads, validates, or deducts stock. Cancel never restores stock.

Example (your case): stock 10 → bill qty 5 succeeds (stock stays 10 in practice today, or stays unchanged) → bill qty 6 also succeeds because billing ignores stock entirely.

Confirmed: **zero** `stock_quantity` references in `bill_service.py`.

---

## 3. Existing stock database design

| Field | Status |
|-------|--------|
| `items.stock_quantity` | Exists — `DECIMAL(12,3) NULL` (NULL = not tracked) |
| `chk_items_stock` | `stock_quantity IS NULL OR >= 0` |
| `minimum_stock_level` | **Does not exist** |
| Stock movements table | **Does not exist** |
| Notifications table | **Does not exist** |

Manual set/clear via Items API/UI only (`ItemService`).

---

## 4. Existing billing transaction flow

`POST /bills` = create + finalize in one transaction:

1. Auth context (tenant/user)  
2. Merge lines; qty > 0  
3. Load items (tenant + active)  
4. Server money calc  
5. Lock bill-number counter (`FOR UPDATE`)  
6. Insert bill `FINALIZED` + bill_items  
7. Audit `CREATE_BILL`  
8. Commit  

**Missing:** stock lock / check / deduct.

**Cancel:** status → `CANCELLED` + audit; **no stock restore** today.

---

## 5. Existing notification architecture

| Kind | Status |
|------|--------|
| In-app notifications (bell, unread) | **None** |
| Login email notify | Optional env flag only |
| Audit activity alerts | Computed `GET /audit-logs/alerts` (owner); not stock-related; no read state |

Must **add** a proper `notifications` feature for low/out-of-stock (plus API + bell UI).

---

## 6. Proposed sprint plan (one sprint)

**Sprint name:** P3-1 — AI crash fix + Stock enforcement + Low-stock notifications  

### A. AI page (small, first)

1. Import `Card`, `CardContent`.  
2. Harden UI states: Loading (“Analyzing…”), Empty (insufficient data), Error + **Retry**, Success — never blank.  
3. Optional: light ErrorBoundary around owner outlet (recommended).  
4. Reconfirm tenant isolation (existing tests + spot check).

### B. Stock enforcement (backend = authority)

**Rule:** If `stock_quantity IS NULL` → untracked (no check/deduct). If set → enforce.

1. Add `items.minimum_stock_level` (nullable DECIMAL) via Alembic + `02_schema.sql` + apply script.  
2. **Atomic bill create** (same DB transaction):  
   - Lock items `FOR UPDATE` (stable `item_id` order)  
   - Validate qty ≤ stock for tracked items  
   - Reject with existing API error shape + clear message  
     (`Insufficient stock. Available: 5, requested: 6.` / out-of-stock)  
   - Deduct stock → create bill + lines → audit (`CREATE_BILL` + `STOCK_DEDUCTED`) → commit  
3. **Cancel restore:** On cancel, restore deducted qty for tracked items + audit `STOCK_RESTORED` (cancel already exists).  
4. Concurrency: row locks so two bills cannot oversell the same units.  
5. FE `NewBillPage`: show Available stock; block invalid qty; surface backend error; disable/prevent Generate when cart invalid.  
6. Items UI: edit `minimum_stock_level`.  
7. Consistent threshold rule: **notify when `stock_quantity <= minimum_stock_level`** (document in tests).

### C. Notifications (new)

1. Table `notifications` (tenant_id required; user_id nullable = whole tenant; type, title, message, entity_*, is_read, timestamps).  
2. APIs: list, unread-count, mark read, mark-all-read (JWT + tenant scope; Owner + Billing User).  
3. Writers on stock transitions only (duplicate control):  
   - `LOW_STOCK` when crossing into `<= minimum`  
   - `OUT_OF_STOCK` when hitting 0  
   - Optional `INSUFFICIENT_STOCK_ATTEMPT` on rejected bill (low volume)  
4. Bell + Badge + Popover in **OwnerLayout** and **BillingLayout**.  
5. Isolation tests: Business A ↛ Business B.

### D. Docs + tests

- Pytest: AI page regression not needed; stock reject/deduct/cancel restore/concurrency; notification dup + isolation.  
- Update `docs/test-business-billing-guide.md` with Rice 10 / min 5 scenarios.  
- Update DB docs.

### Explicitly out of this sprint

- Rebuild AI algorithms / charts  
- Full inventory module (purchase orders, warehouses)  
- Push/email for every stock change  
- Changing bill money / GST rules  

---

## 7. Acceptance checklist (after implementation)

- [ ] `/owner/ai` never blank (load / empty / error / success)  
- [ ] Stock cannot go negative; oversell rejected on backend  
- [ ] Multi-item bill all-or-nothing  
- [ ] Concurrent bills cannot oversell  
- [ ] Cancel restores stock when tracked  
- [ ] Low / out-of-stock notifications + unread/read  
- [ ] Tenant isolation for AI + notifications + stock  
- [ ] Existing billing/reports still green  

---

## 8. Approval gate

**No code will be changed until you approve.**

Should I start this sprint?
