# Phase 2 Sprint P2-11 — Audit + item activity verification

**Date:** 2026-08-14  
**Goal:** LOGIN / CREATE_BILL / item create-edit-deactivate visible to Owner after Billing User actions.  
**Result:** **PASS** — no application code changes required.

---

## Automated suites

```text
.\.venv\Scripts\python -m pytest tests/test_p2_11_audit_item_activity.py tests/test_audit_logs.py tests/test_billing_item_management.py -q
```

| Suite | Result |
|-------|--------|
| `test_p2_11_audit_item_activity.py` | ✅ Pass (end-to-end Owner visibility) |
| `test_audit_logs.py` | ✅ Pass (LOGIN/CREATE_BILL, cancel detail, isolation, survive deactivate) |
| `test_billing_item_management.py` | ✅ Pass (billing CRUD + owner filters + no hard delete) |
| **Total** | **18 passed** |

---

## Guided checks

| Scenario | Expected | Result |
|----------|----------|--------|
| Billing User logs in | Owner sees `LOGIN` for that `user_id` | ✅ |
| Billing User finalizes bill | Owner sees `CREATE_BILL` + bill number | ✅ |
| Billing creates / edits / deactivates item | Owner Item Activity (`entity_type=ITEM`) shows `ITEM_CREATED`, `ITEM_UPDATED`, `ITEM_DEACTIVATED` | ✅ |
| Soft-deactivate | Active catalog hides item; audit detail keeps name + reason | ✅ |
| Billing User opens audit API | 403; no delete endpoint | ✅ |
| Cross-tenant audit | Hotel B cannot see Hotel A cancel/create rows | ✅ (existing) |

### FE wiring (confirmed)

| UI | API |
|----|-----|
| Owner **Audit** | `/audit-logs` (+ filters / detail / alerts) |
| Owner **Item Activity** | `/audit-logs?entity_type=ITEM` |
| Owner dashboard recent item activity | `/audit-logs?entity_type=ITEM&per_page=6` |

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| LOGIN visible to Owner after Billing User login | ✅ |
| CREATE_BILL visible to Owner | ✅ |
| Item create / edit / deactivate visible | ✅ |
| History survives deactivate | ✅ |
| Fixes only if regressions | ✅ N/A |
