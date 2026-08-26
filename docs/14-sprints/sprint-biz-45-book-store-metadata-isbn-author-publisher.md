# Sprint BIZ-45 – Book Store Metadata – ISBN Author Publisher

## Objective

Book-specific item metadata and search.

## Business Type

Book Stores

## Why This Sprint Is Required

ISBN/author/publisher special.

## Existing Functionality

Items + barcode.

## Missing Functionality

book metadata fields/search.

## Scope

### Backend Tasks

- Book attributes
- Search by ISBN/author

### Frontend Tasks

- Book form + search

### Database Tasks

- item book fields or JSON

### API Tasks

- search

### UI/UX Tasks

- Book catalog

### Testing Tasks

- ISBN unique per tenant

### Documentation Tasks

- 12-book-stores

## Database Changes

Conceptual entities only (no SQL in this plan):

- book attributes

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /items search

## Frontend Pages

- BooksCatalog

## User Roles

Owner catalog; Billing sell.

## Tenant Isolation

ISBN unique per tenant.

## Audit Requirements

Catalog changes.

## Notifications

None.

## Acceptance Criteria

- ISBN search works

## Dependencies

BIZ-44

## Risks

- None

## Definition of Done

- Metadata complete

## Status

COMPLETED

## Deliverables

- Columns on `items`: `isbn` (unique per tenant), `author`, `publisher`
- Migration: `20260826_biz45_book_store_metadata`
- Search: `/items?q=` matches ISBN/author/publisher; `/items?isbn=` exact; `/books/catalog`, `/books/by-isbn/<isbn>`
- UI: Items form + list + search label gated by `book_metadata`
- Tests: `test_biz45_book_store_metadata.py` (5 passed)

## Phase

Phase 08 – Stationery / Books
