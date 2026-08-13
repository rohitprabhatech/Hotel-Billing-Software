# 12 — Bill Printing

## Purpose

Produce an Indian restaurant **thermal / cash-memo** style receipt suitable for 58mm and 80mm printers via browser print CSS.

## Components

| Component | Responsibility |
|-----------|----------------|
| `BillPreview.jsx` | On-screen preview inside app |
| `PrintableReceipt.jsx` | Print-only layout; no dashboard chrome |
| Print route / window | Isolated view for `window.print()` |

Keep printing logic separate from owner/billing dashboards.

## Dynamic Header Fields (from `tenants`)

- Business / hotel name
- Address, city, pincode
- Phone
- GSTIN
- FSSAI number (if configured)

Do **not** hard-code hotel identity.

## Receipt Body Fields (from `bills` / `bill_items`)

- Date / time
- Bill number
- Table number (if present)
- Employee / billing user name or code
- Line items: Particulars, Qty, Rate, Amount
- Sub Total
- Discount (if any)
- CGST @ x% On taxable
- SGST @ x% On taxable
- Food / Grand Total (with optional round-off display)
- Footer: Thank You / Visit Again
- Optional guest note (e.g., party size) if stored later

## Layout Requirements

- Black-and-white friendly
- Clear alignment of Qty / Rate / Amount columns
- Readable monospace or compact sans for thermal width
- No browser UI chrome in print (`@media print` hide nav/buttons)
- Print only the receipt

## Width Support

```text
58mm  → narrower CSS width / font size
80mm  → default recommended width
```

Provide a width toggle or CSS class (`receipt--58`, `receipt--80`) where practical.

## Sample Structure (Illustrative)

```text
              {business_name}
            {address}
              {city}/{pincode}
              {phone}

        -------------------------
              Cash Memo
        -------------------------

Date : {date}       Bill No. : {bill_number}
T. No.: {table}      Emp. : {user}

-----------------------------------------
Particulars       Qty    Rate    Amount
-----------------------------------------
{lines...}
-----------------------------------------
Sub Total :                      {subtotal}
Discount :                       {discount}
CGST @ {r}% On {taxable} :       {cgst}
SGST @ {r}% On {taxable} :       {sgst}
-----------------------------------------
Total :                          {grand_total}
-----------------------------------------
GSTIN: {gstin}
FSSAI NO: {fssai}

                 Thank You
                Visit Again
```

Exact spacing tuned during Sprint 6 against reference image.

## Print Flow

```text
User clicks Print
  → open print view with bill id
  → fetch bill (tenant-scoped)
  → render PrintableReceipt
  → trigger print dialog
  → notify backend print event
  → audit PRINT_BILL or REPRINT_BILL
```

## Reprint

- Allowed for Owner and Billing User (if permitted)
- Must not alter bill financial data
- Increment `printed_count`
- Visible in owner audit / alerts when frequent

## Non-Goals

- Direct ESC/POS binary driver integration (optional future)
- Payment QR / UPI gateway (out of scope this version)
