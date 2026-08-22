# Phase 07 – Subscription

## 1. Phase objective

Plans, trial, expiry, payments

## 2. Scope

In scope: deliverables listed below for this phase only.  
Out of scope: Medical Store / pharmacy features; coding until documentation is approved.

## 3. Prerequisites

Phase 06

## 4. Deliverables

- Documentation and (post-approval) implementation artifacts for: Subscription
- Related sprints: Sprint 09

## 5. Modules involved

Common Core and/or Master Admin / Subscription / Industry packs as mapped in [phase-sprint-mapping.md](./phase-sprint-mapping.md).

## 6. Database impact

Documented in [../03-database/](../03-database/). No schema apply until coding is approved.

## 7. Backend impact

Flask services/controllers as required by related sprints — **not started** until approval.

## 8. Frontend impact

React pages/layouts per related sprints — **not started** until approval.

## 9. API impact

Documented under [../07-api/](../07-api/).

## 10. Security considerations

Tenant isolation, Master vs tenant auth, audit logging. See [../02-architecture/07-security-architecture.md](../02-architecture/07-security-architecture.md).

## 11. Testing requirements

Strategy in [../10-testing/](../10-testing/); guides in [../12-testing-guides/](../12-testing-guides/).

## 12. Acceptance criteria

- Phase documentation complete and reviewed
- Related sprints have clear DoD
- No Medical Store scope included
- Traceability rows exist in [../00-project-foundation/07-requirements-traceability.md](../00-project-foundation/07-requirements-traceability.md)

## 13. Related sprints

Sprint 09

## 14. Dependencies

Phase 06

## 15. Completion criteria

All related sprints marked COMPLETED in [../14-sprints/sprint-tracker.md](../14-sprints/sprint-tracker.md) and gate tests pass.
