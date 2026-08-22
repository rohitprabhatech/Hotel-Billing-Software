# Phase ↔ Sprint Mapping

## A. Platform foundation (historical docs plan)

| Phase | Name | Sprints |
|---|---|---|
| 00 | Discovery and Analysis | Sprint 00 |
| 01 | Foundation | Sprint 01, Sprint 02 |
| 02 | Database | Sprint 03 |
| 03 | Authentication and Tenancy | Sprint 04 |
| 04 | Common Billing | Sprint 05, Sprint 06 |
| 05 | Business Modules | Sprint 07 |
| 06 | Master Admin | Sprint 08 |
| 07 | Subscription | Sprint 09 |
| 08 | AI and Integrations | Sprint 10, Sprint 11 |
| 09 | Testing and Security | Sprint 12, Sprint 13 |
| 10 | Production Readiness | Sprint 14 |

Note: Much of the platform foundation is **already implemented**. Industry work uses the BIZ plan below.

## B. Business-specific development (active)

| Phase | Name | Sprints |
|---|---|---|
| 01 | Common Platform Readiness | BIZ-01 … BIZ-10 |
| 02 | Restaurant / Cafe | BIZ-11 … BIZ-19 |
| 03 | Grocery / Retail | BIZ-20 … BIZ-24 |
| 04 | Clothing | BIZ-25 … BIZ-28 |
| 05 | Mobile / Electronics | BIZ-29 … BIZ-34 |
| 06 | Hardware / Building Material | BIZ-35 … BIZ-39 |
| 07 | Bakery / Food Production | BIZ-40 … BIZ-43 |
| 08 | Stationery / Books | BIZ-44 … BIZ-46 |
| 09 | Furniture | BIZ-47 … BIZ-50 |
| 10 | Wholesale | BIZ-51 … BIZ-55 |
| 11 | Travel Agency | BIZ-56 … BIZ-60 |
| 12 | Cross-Business Reports / AI / Notifications | BIZ-61 … BIZ-63 |
| 13 | Security / Testing / Performance | BIZ-64 … BIZ-66 |
| 14 | Production Readiness | BIZ-67 … BIZ-68 |

Full tracker: [../14-sprints/sprint-tracker.md](../14-sprints/sprint-tracker.md)

**Separation of concerns**

| Concept | Answers | Location |
|---|---|---|
| Business docs | What does this business need? | `05-businesses/` |
| Phase docs | When / what stage do we build it? | `13-phases/` + `14-sprints/business-development-phases.md` |
| Sprint docs | What exact work do developers perform? | `14-sprints/sprint-biz-*.md` |

Example: Restaurant Table Management → Business `01-hotels-restaurants` → Business Phase 02 → Sprint **BIZ-12**.
