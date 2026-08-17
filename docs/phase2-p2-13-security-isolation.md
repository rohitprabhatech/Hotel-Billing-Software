# Phase 2 Sprint P2-13 — Security + tenant isolation retest

**Date:** 2026-08-14  
**Goal:** Business A ↛ Business B for categories / items / bills / reports / users / audit / activity.  
**Baseline:** [`security-tenant-audit.md`](./security-tenant-audit.md) (Sprint 21)  
**Result:** **PASS** — no application code changes; Sprint 21 hardening still holds.

---

## Automated suites

```text
.\.venv\Scripts\python -m pytest ^
  tests/test_p2_13_tenant_isolation_matrix.py ^
  tests/test_tenant_isolation.py ^
  tests/test_security_hardening.py ^
  tests/test_audit_logs.py::test_cross_tenant_audit_isolation ^
  tests/test_reports.py::test_cross_tenant_report_isolation ^
  tests/test_billing.py::test_cross_tenant_bill_access_denied ^
  tests/test_categories_items.py::test_cross_tenant_category_isolation ^
  tests/test_ai_assistant.py::test_ai_analysis_tenant_isolation ^
  tests/test_ai_assistant.py::test_decisions_tenant_isolation -q
```

| Suite | Result |
|-------|--------|
| `test_p2_13_tenant_isolation_matrix.py` | ✅ Pass (full A↛B matrix) |
| `test_tenant_isolation.py` | ✅ Pass |
| `test_security_hardening.py` | ✅ Pass (logout/deactivate revoke, email unique, IDOR, audit immutable) |
| Cross-tenant spot checks (audit/reports/bills/categories/AI) | ✅ Pass |
| **Total** | **23 passed** |

---

## Isolation matrix (Business A ↛ Business B)

| Surface | Cross-tenant probe | Expected | Result |
|---------|-------------------|----------|--------|
| Categories | GET / list foreign id | 404 / absent from list | ✅ |
| Items | GET foreign id; bill with foreign `item_id` | 404 / 400–404 | ✅ |
| Bills | GET / cancel foreign id; list | 404 / id absent | ✅ |
| Reports | Summary today | Only own sales | ✅ |
| Users | List / GET foreign id | No foreign emails / 404 | ✅ |
| Audit | Detail of foreign log; CREATE_BILL by `entity_id` | 404 / no foreign bill ids | ✅ |
| Item activity | `entity_type=ITEM` scoped | Own create only; detail IDOR 404 | ✅ |
| AI | Analysis / decisions | Tenant-scoped (existing) | ✅ |

**Note:** Display `bill_number` can collide across tenants (per-tenant sequences). Isolation is enforced by `tenant_id` + bill/entity **id**, not by bill_number string alone.

---

## Delta vs Sprint 21

| Sprint 21 finding | P2-13 status |
|-------------------|--------------|
| S21-01 Logout revokes JWT | ✅ Still green |
| S21-02 Global email uniqueness | ✅ Still green |
| S21-03/04 Token invalidation | ✅ Still green |
| S21-05 Deactivate revokes JWT | ✅ Still green |
| S21-06 Proxy IP trust gated | ✅ Unchanged (accepted design) |
| S21-07 JWT TTL documented | ✅ Unchanged residual |
| S21-08 Audit API immutable | ✅ Still green |
| S21-09 Dev tokens | ✅ Accepted |
| S21-10 Isolation / RBAC / bill totals | ✅ Reconfirmed + matrix test added |
| **New Critical / High regressions** | **None** |

### Residual follow-ups (unchanged, non-blocking)

1. Optional DB unique index on `users.email`  
2. Shorter production JWT TTL / refresh tokens  
3. DB triggers to block SQL mutation of `audit_logs`  
4. Stronger password complexity  

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Automated isolation matrix green | ✅ |
| Sprint 21 controls still hold | ✅ |
| Delta documented | ✅ |
| Business A ↛ Business B | ✅ |
| Fixes only if regressions | ✅ N/A |
