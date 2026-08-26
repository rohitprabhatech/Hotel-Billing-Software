# Sprint BIZ-54 – Wholesale Outstanding Challan and GST Invoice

## Objective

Outstanding reports, challan, GST invoice using existing bill PDF + credit.

## Business Type

Wholesale Shops

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- `GET /api/v1/reports/outstanding` — FIFO-aged customer + supplier dues (0–30 / 31–60 / 61–90 / 90+)
- Alias: `GET /api/v1/wholesale/reports/outstanding`
- Wholesale challan aliases: `/wholesale/challans` (+ PDF)
- Bill PDF: **TAX INVOICE** title when GST / wholesale / GSTIN; line GST %; place of supply

### Frontend

- `/owner/outstanding` — aged outstanding table + print
- Nav: Outstanding Report (customer_credit module)

### Tests

- `backend/tests/test_biz54_wholesale_outstanding.py` (4 passed)

## Acceptance Criteria

- [x] Customer + supplier outstanding (aged)
- [x] Reports live
- [x] Challan usable via wholesale aliases
- [x] GST tax invoice PDF polish

## Dependencies

BIZ-53, BIZ-37

## Next

BIZ-55 — wholesale testing gate
