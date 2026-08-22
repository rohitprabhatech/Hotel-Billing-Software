# 11 — Billing Workflow

## Goals

- Fast counter billing for Billing User
- Backend-authoritative money math
- Atomic finalize
- Historical price/GST snapshots
- Cancel/void without hard delete

## Actors

- Billing User (primary)
- Owner (may also bill)

## Happy Path — Create Bill

```text
1. Open New Bill screen
2. Search/select active items
3. Add lines; adjust qty; remove mistakes; clear draft (client-side cart)
4. Apply permitted discount (if any)
5. Submit cart to POST /api/v1/bills
6. Server:
   a. Validate items belong to tenant and are active
   b. Lock/allocate next bill_sequence for tenant
   c. Snapshot each line (name, unit_price, gst_percentage)
   d. Calculate:
        Subtotal
        Discount
        Taxable Amount
        CGST
        SGST
        GST Amount
        Grand Total (+ optional round_off)
   e. Insert bills + bill_items in one transaction
   f. Write audit CREATE_BILL
   g. Commit
7. Return bill payload for preview/print
8. User prints receipt → POST print endpoint → PRINT_BILL audit
```

## Client Cart vs Server Bill

| Stage | Storage |
|-------|---------|
| Before submit | Frontend cart only (not trusted) |
| After finalize | Database `FINALIZED` bill |

Optional server-side `DRAFT` bills may be added later; v1 can finalize in one POST from cart.

## Draft Editing Rules (Client Cart)

Allowed before finalize:

- Add item
- Change quantity (> 0)
- Remove line
- Clear current bill
- Apply discount within configured max (if any)

Not allowed after finalize:

- Silent line edits
- Hard delete
- Changing historical prices

## Calculation Rules (Server)

Use `Decimal` throughout.

Illustrative model (confirm during implementation; keep consistent):

```text
line_gross     = unit_price * quantity
bill_subtotal  = sum(line_gross)
discount       = requested discount (validated ≥ 0, ≤ subtotal / policy max)
taxable        = subtotal - discount
# GST: for v1, apply bill-level or line-level GST; prefer line-level snapshots
# Example line-level:
line_taxable   = allocate discount proportionally OR apply item gst on (unit_price * qty)
cgst           = taxable * (gst_rate/2) / 100
sgst           = taxable * (gst_rate/2) / 100
grand_total    = taxable + cgst + sgst
```

If items have different GST rates, compute per line then sum CGST/SGST.

**Never trust** React-provided totals.

## Bill Number Generation

```text
BEGIN TRANSACTION
  lock bill_number_counters row for tenant
  n = next_value
  next_value = n + 1
  bill_number = format(prefix, n)  # e.g. "57" or "INV-2026-000057"
COMMIT with bill insert
```

UNIQUE `(tenant_id, bill_number)` prevents duplicates under race conditions.

## Cancel / Void Flow

```text
FINALIZED bill
    → Cancellation request + reason (required)
    → Authorization check
    → Status = CANCELLED (or VOID)
    → cancelled_by, cancelled_at, cancellation_reason set
    → Audit CANCEL_BILL / VOID_BILL with amounts
    → Original lines remain
```

Owner can review cancelled bills forever (within retention policy).

## Remove Accidentally Added Item

Applies **only** to the current cart (pre-finalize):

```text
Remove Item | Change Quantity | Clear Current Bill
```

After finalize, correction path is **cancel** (and optionally create a new bill)—not silent edit.

## Print / Reprint

```text
GET bill detail (includes tenant header fields)
→ render PrintableReceipt
→ window.print()
→ POST /bills/{id}/print → increments printed_count, audit PRINT_BILL or REPRINT_BILL
```

## Failure Handling

| Failure | Behavior |
|---------|----------|
| Inactive item in cart | 400; bill not created |
| Discount invalid | 400 |
| Concurrent bill number | Retry or unique violation → safe error |
| Mid-transaction DB error | Full rollback |

## Acceptance Checks

- Historical bill shows old price after item price change
- Cancelled bill still listed for owner with reason
- Two parallel finalize requests get distinct bill numbers
- Billing User cannot call a delete-bills endpoint (none exists)
