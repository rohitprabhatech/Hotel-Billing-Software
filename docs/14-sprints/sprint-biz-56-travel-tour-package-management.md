# Sprint BIZ-56 – Travel Tour Package Management

## Objective

Tour packages with pricing (service-oriented, not classic SKU stock).

## Business Type

Travel Agencies

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- Table: `tour_packages` (code, name, destination, duration, price, GST, linked `item_id`)
- Migration: `20260826_biz56_tour_packages`
- Linked catalog item always has `stock_quantity=NULL` (no stock checks / deductions)
- APIs: `/tour-packages` and aliases `/travel/packages`
- `POST .../packages/{id}/bill` — service billing helper
- Auto category **Tour Packages** for linked items

### Frontend

- `/owner/tour-packages` — package cards, create/edit, Create bill

### Tests

- `backend/tests/test_biz56_tour_packages.py` (5 passed)

## Acceptance Criteria

- [x] Packages billable without negative stock
- [x] Service billing path clear (linked untracked item + `/bill`)

## Dependencies

BIZ-10, BIZ-04

## Next

BIZ-57 — travel booking management and payments
