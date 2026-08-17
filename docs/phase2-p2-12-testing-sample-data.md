# Phase 2 Sprint P2-12 — Testing docs + sample data

**Date:** 2026-08-14  
**Goal:** Step-by-step manual with **exact** entries.  
**Result:** **PASS** — docs updated; no application code changes.

---

## Sample business (canonical)

| Field | Exact value |
|-------|-------------|
| Business | Shree General Store · Grocery Store |
| Owner | Rajesh Patil · `owner@example.com` · `Owner@12345` |
| Billing | Amit Sharma · `billing@example.com` · `Billing@12345` |
| Categories | Grocery → Rice, Pulses; Beverages → Cold Drinks |
| Items (5% GST) | Rice 5kg ₹450; Dal 1kg ₹140; Cold Drink 750ml ₹50; Biscuits ₹30 |
| Bills | Cash Rice+Dal (`C-1` → ₹620); Online Cold Drink×2 after removing Biscuits (`C-2` → ₹105) |

---

## Deliverables updated

| Document | Change |
|----------|--------|
| [`test-business-billing-guide.md`](./test-business-billing-guide.md) | §A exact pack + **Script G** checklist; coverage map includes P2-9…P2-11 tests |
| [`owner-manual.md`](./owner-manual.md) | Practice sample table |
| [`billing-user-manual.md`](./billing-user-manual.md) | Counter practice bills |
| [`user-manual.md`](./user-manual.md) | Link to QA sample |
| [`docs/README.md`](./README.md) | Index links for Phase 2 verification notes |

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Exact sample business / users / catalog documented | ✅ |
| Cash + Online + remove Biscuits before finalize | ✅ |
| Manuals aligned | ✅ |
| Fixes only if regressions | ✅ N/A (docs only) |
