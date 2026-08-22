# Phase 2 Sprint P2-10 — Reports + dashboard verification

**Date:** 2026-08-14  
**Goal:** Today / week / month totals match manual calc on sample bills.  
**Result:** **PASS** — no application code changes required.

---

## Automated suites

```text
.\.venv\Scripts\python -m pytest tests/test_p2_10_reports_reconciliation.py tests/test_reports.py -q
```

| Suite | Result |
|-------|--------|
| `test_p2_10_reports_reconciliation.py` | ✅ Pass (manual reconciliation + billing-home align) |
| `test_reports.py` | ✅ Pass (owner access, periods, cancel exclude, isolation, export) |
| **Total** | **10 passed** |

---

## Sample reconciliation (isolated tenant)

Hand calc uses the same server rules as billing: line GST after discount; **grand total rounds to nearest ₹**.

| Bill | Payment | Lines | Discount | Pre-round | Grand | Counts in sales? |
|------|---------|-------|----------|-----------|-------|------------------|
| A | cash | Rice ₹100 × 2 @ 5% GST | 0 | ₹210.00 | **₹210** | Yes |
| B | online | Oil ₹200 × 1 @ 5% GST | ₹10 | ₹199.50 | **₹200** | Yes |
| C | cash | Rice ₹100 × 1 | 0 | — | — | **No** (cancelled) |

### Expected metrics (today = this_week = this_month for same-day sample)

| Metric | Expected |
|--------|----------|
| `bill_count` | 2 |
| `total_sales` | **₹410** (210 + 200) |
| `cash_sales` / `cash_bill_count` | ₹210 / 1 |
| `online_sales` / `online_bill_count` | ₹200 / 1 |
| `cancelled_bills` | 1 |
| `average_bill` | ₹205.00 |

Asserted via `GET /api/v1/reports/summary?period=today|this_week|this_month` and `GET /api/v1/reports/weekly-sales`.

### Billing home KPI

`GET /api/v1/bills/today-summary` matches report **today** `total_sales` / `bill_count` on a second isolated sample (Salt ₹50 × 3 @ 0% GST → ₹150).

---

## Dashboard wiring (confirmed)

| UI | API |
|----|-----|
| Owner dashboard / reports | `/reports/summary`, `/reports/weekly-sales` |
| Billing home today KPI | `/bills/today-summary` |

All three share the same rules: **FINALIZED** `grand_total` only; cancelled excluded from sales; Asia/Kolkata day/week/month bounds.

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Today totals = manual sample | ✅ |
| Week totals = manual sample | ✅ |
| Month totals = manual sample | ✅ |
| Cancelled excluded from `total_sales` | ✅ |
| Dashboard / billing home agree with reports | ✅ |
| Documented reconciliation | ✅ |
| Fixes only if regressions | ✅ N/A |
