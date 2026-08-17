# Phase 2 Sprint P2-9 — Billing + payment verification

**Date:** 2026-08-14  
**Goal:** Cash/Online, remove-from-cart, totals, print/cancel still correct.  
**Result:** **PASS** — no application code changes required.

---

## Automated suites

```text
pytest tests/test_billing.py tests/test_print_cancel.py tests/test_p2_9_billing_verification.py -q
```

| Suite | Result |
|-------|--------|
| `test_billing.py` | ✅ Pass (finalize totals, reference, cash/online, filters) |
| `test_print_cancel.py` | ✅ Pass (cancel+reason, print/reprint audit, search) |
| `test_p2_9_billing_verification.py` | ✅ Pass (Biscuits cart omit, online+discount+round-off) |
| **Total** | **15 passed** |

---

## Guided checks

| Scenario | Expected | Result |
|----------|----------|--------|
| Finalize bill; server ignores client `grand_total` | Server calc wins | ✅ `test_finalize_bill_server_totals` |
| Cash default + explicit Cash / Online | Labels + list/report filters | ✅ `test_payment_method_cash_and_online` |
| Remove Biscuits from cart, bill only Tea | Catalog **Biscuits** stays active | ✅ FE `removeLine` is cart-only; API omit-line test |
| Online bill with discount | Subtotal/discount/taxable; grand rounds to ₹ | ✅ |
| Cancel requires reason; record kept | Status CANCELLED; items retained | ✅ |
| Print then reprint | `printed_count` 1→2; audit actions | ✅ |
| Cancelled bill still printable/readable | Status + tenant + line snapshots | ✅ |

### FE cart remove (manual note)

`NewBillPage.removeLine` only filters React cart state. Tooltip: *“Remove from bill (does not delete catalog item)”*. No item DELETE/status API is called.

---

## Totals convention (confirmed)

- Line GST after proportional discount allocation  
- **Grand total rounds to nearest rupee** (`round_off` holds the difference)  
- Example: Tea ₹15 × 2 @ 5% GST → ₹31.50 pre-round → **₹32.00**

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Cash/Online correct | ✅ |
| Remove-from-cart ≠ catalog delete | ✅ |
| Totals correct (incl. round-off) | ✅ |
| Print / cancel correct | ✅ |
| Guided sample bills documented | ✅ |
| Fixes only if regressions | ✅ N/A |
