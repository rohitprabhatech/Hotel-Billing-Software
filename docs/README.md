# Prabha Billing SaaS — Documentation

**Provider:** Prabha Technology Pvt. Ltd.

## READ THIS FIRST

This folder is the **single structured documentation system** for the product.

1. Do **not** start coding until documentation is approved.
2. There is **one source of truth** per topic under the numbered folders below.
3. Historical Phase/Sprint reports and old flat docs live in [`archive/`](./archive/) — do not treat them as the active plan.
4. **Medical Store is permanently excluded.** Fourteen business types only.
5. Business docs ≠ Phase docs ≠ Sprint docs (see mapping below).

### Recommended reading order

1. [Project Overview](./00-project-foundation/01-project-overview.md)
2. [Functional Requirements](./01-requirements/01-functional-requirements.md)
3. [Business packs](./05-businesses/)
4. [System Architecture](./02-architecture/01-system-architecture.md)
5. [Database Overview](./03-database/01-database-overview.md)
6. [Common Modules](./04-common-modules/)
7. [Business Modules](./05-businesses/)
8. [API Overview](./07-api/01-api-overview.md)
9. [UI/UX](./08-ui-ux/01-design-system.md)
10. [Master Admin](./06-master-admin/01-master-dashboard.md)
11. [Subscription](./09-subscription/01-subscription-overview.md)
12. [Testing](./10-testing/01-testing-strategy.md)
13. [Phases](./13-phases/project-roadmap.md)
14. [Sprints](./14-sprints/sprint-tracker.md)

Also: [Documentation Status](./documentation-status.md) · [Requirements Traceability](./00-project-foundation/07-requirements-traceability.md) · [Full Audit Report](./DOCUMENTATION_AUDIT_REPORT.md) · [Business Sprint Plan](./14-sprints/business-sprint-plan-overview.md) · [Module Feature Matrix](./00-project-foundation/09-module-feature-matrix.md)

---

## Where to start

| Need | Go to |
|---|---|
| What is the product? | `00-project-foundation/` |
| What must we build? | `01-requirements/` |
| How is it built? | `02-architecture/` |
| Data model | `03-database/` |
| Shared features | `04-common-modules/` |
| Industry needs | `05-businesses/` |
| Platform ops | `06-master-admin/` |
| HTTP APIs | `07-api/` |
| Screens / UX | `08-ui-ux/` |
| Plans & trial | `09-subscription/` |
| How we test | `10-testing/` + `12-testing-guides/` |
| End-user help | `11-user-manual/` |
| When we build | `13-phases/` |
| Exact sprint work | `14-sprints/` |
| Old reports | `archive/` |

## Structure

```
docs/
├── 00-project-foundation/
├── 01-requirements/
├── 02-architecture/
├── 03-database/
├── 04-common-modules/
├── 05-businesses/          # 14 industries (no Medical)
├── 06-master-admin/
├── 07-api/
├── 08-ui-ux/
├── 09-subscription/
├── 10-testing/
├── 11-user-manual/
├── 12-testing-guides/
├── 13-phases/
├── 14-sprints/
├── archive/
├── documentation-status.md
└── README.md
```

## Business vs Phase vs Sprint

| | Business | Phase | Sprint |
|---|---|---|---|
| Question | What does this business need? | When / what stage? | What exact work? |
| Example | Restaurant tables | Phase 05 Business Modules | Sprint 07 |

See [13-phases/phase-sprint-mapping.md](./13-phases/phase-sprint-mapping.md).
