# Phase 2 Sprint P2-8 — Performance notes

**Date:** 2026-08-14  
**Goal:** Fix measured bottlenecks only (no broad rewrite).

---

## Before → After

| Bottleneck | Before | After |
|------------|--------|-------|
| Item list N+1 | Lazy `item.category` / `item.creator` + hierarchy walk per row | `joinedload(category, creator)` + one tenant category map for `hierarchy_path` |
| Items / bills pages | Hard `per_page=100` dump | Paginated UI (`25` / page) via existing API `meta` |
| Initial JS bundle | Eager import of all app pages (~1.1MB single chunk) | Route-level `React.lazy` for owner/billing/auth heavy pages |
| Billing catalog typing | Search on every keystroke / button only | 250ms debounce + `per_page=100` active catalog |
| Report/dashboard bills | Separate `(tenant,status)` and `(tenant,created_at)` indexes | Added composite `ix_bills_tenant_status_created_at` |

---

## Measured / verified

| Check | Result |
|-------|--------|
| `pytest tests/test_item_list_performance.py` | Bounded statement count (`< 20` for 12 items) vs N+1 |
| Category/item regression suite | Green |
| Frontend production build | Green; multiple lazy chunks emitted |

---

## Ops

Existing DBs:

```text
python scripts/apply_pending_schema.py
# or specifically: python scripts/apply_bill_report_index.py
```

Alembic: `20260814_bill_report_index` (after `20260814_category_parent_key`).

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Item list N+1 fixed | ✅ |
| FE pagination for items/bills | ✅ |
| Route code splitting | ✅ |
| Index review for report hot path | ✅ |
| Billing catalog search stays responsive | ✅ debounce |
| Before/after notes | ✅ (this file) |
| No functional regressions (tests) | ✅ |
