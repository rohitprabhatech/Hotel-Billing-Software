# Sprint BIZ-04 – Customer Master (CRM)

## Objective

Add tenant-scoped customer master; link bills to customers without losing ad-hoc name/phone.

## Business Type

All (common core)

## Why This Sprint Is Required

All 14 businesses need CRM; today only bill-level name/phone/email.

## Existing Functionality

Bill customer fields; WhatsApp/email delivery uses bill contact.

## Missing Functionality

customers table, CRUD, search, purchase history link.

## Scope

### Backend Tasks

- Customer model/service
- Link optional customer_id on bills
- Search by phone/name

### Frontend Tasks

- Customers list/form
- Bill picker to attach customer

### Database Tasks

- customers; bills.customer_id nullable FK

### API Tasks

- CRUD /customers
- GET /customers/:id/bills

### UI/UX Tasks

- Standard list+form pages

### Testing Tasks

- Tenant isolation
- Soft-delete history retained via audit

### Documentation Tasks

- 04-common-modules/06-customers

## Database Changes

Conceptual entities only (no SQL in this plan):

- customers (tenant_id, name, phone, email, credit_limit optional, status)

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- GET/POST /customers
- GET/PATCH/DELETE /customers/:id

## Frontend Pages

- /owner/customers
- billing customer picker

## User Roles

Owner/Manager: full CRM. Billing User: create/select on bill.

## Tenant Isolation

All queries filter tenant_id from JWT.

## Audit Requirements

Customer create/update/delete with old/new snapshots.

## Notifications

None required initially.

## Acceptance Criteria

- CRUD works
- Bill can link customer
- Isolation tests pass

## Dependencies

BIZ-01

## Risks

- Duplicate phones — unique per tenant on phone optional

## Definition of Done

- Module usable in Owner+Billing shells

## Status

COMPLETED

## Phase

Phase 01 – Common Platform Readiness
