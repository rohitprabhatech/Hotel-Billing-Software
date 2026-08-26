# Sprint BIZ-50 – Furniture Quotations and Testing Gate

## Objective

Customer quotations (reuse BIZ-36) + testing gate.

## Business Type

Furniture Shops

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- `/api/v1/furniture/quotations` aliases (list, create, get, status, convert) — reuses BIZ-36 quotation module already on `furniture` business type
- No new migration

### Frontend

- Shared **Quotations** page at `/owner/quotations` (module `quotation` already enabled for furniture)

### Tests

- `test_biz50_furniture_quotations.py` (3 passed)
- `test_biz50_furniture_testing_gate.py` (10 passed)
- Full Phase 09: BIZ-47 … BIZ-50 — **28 passed**

### Documentation

- [biz-50-furniture-gate-report.md](./biz-50-furniture-gate-report.md)
- [biz-50-manual-frontend-checklist.md](./biz-50-manual-frontend-checklist.md)

## Acceptance Criteria

- [x] Gate signed

## Dependencies

BIZ-49, BIZ-36

## Phase

Phase 09 – Furniture — **CLOSED**

## Next

BIZ-51 — wholesale pricing matrices (Phase 10)
