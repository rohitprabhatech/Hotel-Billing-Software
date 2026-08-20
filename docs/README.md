# Documentation Index

**Business Billing** — multi-tenant billing SaaS for restaurants, hotels, retail, grocery, and more.  
Software provider: **Prabha Technology Pvt. Ltd.**

Product language prefers **Business** (not Hotel). Hotel remains a supported *business type*.

---

## Start here (current)

Phase 8 (Master Admin + SaaS subscriptions) and the cloud/Master follow-on (**Sprints 1–15**) are **signed off**. Hosted schema is current; **open ops:** seed the first Master Admin when `master_admins` is still empty.

| Document | Description |
|----------|-------------|
| [user-manual.md](./user-manual.md) | Product overview for all roles |
| [owner-manual.md](./owner-manual.md) | Owner console walkthrough |
| [billing-user-manual.md](./billing-user-manual.md) | Billing counter walkthrough |
| [master-admin-manual.md](./master-admin-manual.md) | Prabha Technology Master Admin console |
| [registration-approval-flow.md](./registration-approval-flow.md) | Public register → pending → approve/reject |
| [subscription-management.md](./subscription-management.md) | Trial/paid statuses, renew, cancel, suspend |
| [trial-management.md](./trial-management.md) | Global trial defaults vs per-business trial |
| [plan-management.md](./plan-management.md) | Plan catalog and landing prices |
| [security-architecture.md](./security-architecture.md) | AuthZ, Master vs tenant, audit |
| [tenant-isolation.md](./tenant-isolation.md) | How `tenant_id` is enforced |
| [backup-and-recovery.md](./backup-and-recovery.md) | Inspect, backup, non-destructive upgrade |
| [privacy-policy.md](./privacy-policy.md) | Privacy (canonical page `/privacy`) |
| [terms-of-service.md](./terms-of-service.md) | Terms (canonical page `/terms`) |
| [api-documentation.md](./api-documentation.md) | Current `/api/v1` reference |
| [database-design.md](./database-design.md) | Current data model summary + live status |
| [database-relationships.md](./database-relationships.md) | FK / cascade / isolation |
| [07-database-design.md](./07-database-design.md) | Detailed table catalog (23 tables) |
| [08-database-erd.md](./08-database-erd.md) | Current ERD |
| [deployment-guide.md](./deployment-guide.md) | Local & production deploy |
| [test-business-billing-guide.md](./test-business-billing-guide.md) | Complete E2E / UAT: grocery Script G + Master, trial, plans, expiry, isolation, migration checklist |
| [security-tenant-audit.md](./security-tenant-audit.md) | Sprint 21 security findings + fixes |
| [final-qa-report.md](./final-qa-report.md) | Sprint 22 / Phase 1 release gate |
| [phase2-architecture-audit.md](./phase2-architecture-audit.md) | Phase 2 Sprint P2-1 audit + DB checklist |
| [phase2-p2-3-auth-verification.md](./phase2-p2-3-auth-verification.md) | Phase 2 Sprint P2-3 auth/register verification |
| [phase2-p2-7-responsive-checklist.md](./phase2-p2-7-responsive-checklist.md) | Phase 2 Sprint P2-7 responsive breakpoint checklist |
| [phase2-p2-8-performance.md](./phase2-p2-8-performance.md) | Phase 2 Sprint P2-8 performance before/after notes |
| [phase2-p2-9-billing-verification.md](./phase2-p2-9-billing-verification.md) | Phase 2 Sprint P2-9 billing/payment verification |
| [phase2-p2-10-reports-verification.md](./phase2-p2-10-reports-verification.md) | Phase 2 Sprint P2-10 reports/dashboard verification |
| [phase2-p2-11-audit-verification.md](./phase2-p2-11-audit-verification.md) | Phase 2 Sprint P2-11 audit/item activity verification |
| [phase2-p2-12-testing-sample-data.md](./phase2-p2-12-testing-sample-data.md) | Phase 2 Sprint P2-12 testing docs + sample data |
| [phase2-p2-13-security-isolation.md](./phase2-p2-13-security-isolation.md) | Phase 2 Sprint P2-13 security + tenant isolation retest |
| [phase2-final-qa-report.md](./phase2-final-qa-report.md) | Phase 2 Sprint P2-14 final QA / release gate |
| [development-roadmap.md](./development-roadmap.md) | Active sprint plan & status |
| [phase8-p8-1-architecture-audit.md](./phase8-p8-1-architecture-audit.md) | Phase 8 P8-1 Master Admin / subscription architecture audit |
| [phase8-p8-2-master-auth.md](./phase8-p8-2-master-auth.md) | Phase 8 P8-2 Master Admin auth + `/master` shell |
| [phase8-p8-3-registration-approval.md](./phase8-p8-3-registration-approval.md) | Phase 8 P8-3 Business registration approval |
| [phase8-p8-4-trial-management.md](./phase8-p8-4-trial-management.md) | Phase 8 P8-4 Trial management |
| [phase8-p8-5-plan-management.md](./phase8-p8-5-plan-management.md) | Phase 8 P8-5 Plan management |
| [phase8-p8-6-subscription-lifecycle.md](./phase8-p8-6-subscription-lifecycle.md) | Phase 8 P8-6 Subscription lifecycle + access gate |
| [phase8-p8-7-expiry-notifications.md](./phase8-p8-7-expiry-notifications.md) | Phase 8 P8-7 Expiry notifications + scheduled job |
| [phase8-p8-8-dynamic-landing-pricing.md](./phase8-p8-8-dynamic-landing-pricing.md) | Phase 8 P8-8 Dynamic landing pricing |
| [phase8-p8-9-security-isolation.md](./phase8-p8-9-security-isolation.md) | Phase 8 P8-9 Security + tenant isolation |
| [phase8-p8-10-testing-docs-gate.md](./phase8-p8-10-testing-docs-gate.md) | Phase 8 P8-10 Testing + documentation gate |
| [sprint-1-cloud-db-audit-baseline.md](./sprint-1-cloud-db-audit-baseline.md) | Follow-on Sprint 1 — cloud DB audit baseline |
| [sprint-2-cloud-schema-diff-and-upgrade-plan.md](./sprint-2-cloud-schema-diff-and-upgrade-plan.md) | Follow-on Sprint 2 — schema diff + upgrade plan |
| [sprint-3-live-db-inspection-tooling.md](./sprint-3-live-db-inspection-tooling.md) | Follow-on Sprint 3 — live DB inspection tooling |
| [sprint-4-master-login-ux.md](./sprint-4-master-login-ux.md) | Follow-on Sprint 4 — Master login UX |
| [sprint-5-master-lifecycle-platform-audit.md](./sprint-5-master-lifecycle-platform-audit.md) | Follow-on Sprint 5 — business lifecycle + platform audit |
| [sprint-6-docs-e2e-guide.md](./sprint-6-docs-e2e-guide.md) | Follow-on Sprint 6 — manuals + complete E2E testing guide |
| [sprint-7-master-query-performance.md](./sprint-7-master-query-performance.md) | Follow-on Sprint 7 — Master list/dashboard query performance |
| [sprint-8-live-database-inspect.md](./sprint-8-live-database-inspect.md) | Follow-on Sprint 8 — live inspect of `u583892242_HotelBillingDB` (read-only) |
| [sprint-8-live-schema-inspect.json](./sprint-8-live-schema-inspect.json) | Sprint 8 inspect JSON (no credentials) |
| [sprint-9-live-schema-apply.md](./sprint-9-live-schema-apply.md) | Follow-on Sprint 9 — non-destructive apply of Phase 8 tables |
| [sprint-9-post-apply-inspect.json](./sprint-9-post-apply-inspect.json) | Sprint 9 re-inspect after helpers |
| [sprint-10-master-bootstrap.md](./sprint-10-master-bootstrap.md) | Follow-on Sprint 10 — platform readiness + Master Admin seed tooling |
| [sprint-10-platform-ready.json](./sprint-10-platform-ready.json) | Sprint 10 live readiness JSON (no credentials) |
| [sprint-11-phase8-alembic.md](./sprint-11-phase8-alembic.md) | Follow-on Sprint 11 — Phase 8 Alembic revision + live stamp |
| [sprint-12-final-verification.md](./sprint-12-final-verification.md) | Follow-on Sprint 12 — final verification / signoff |
| [sprint-12-final-verification.json](./sprint-12-final-verification.json) | Sprint 12 live readiness JSON (no credentials) |
| [sprint-13-status-filter-pagination.md](./sprint-13-status-filter-pagination.md) | Follow-on Sprint 13 — status-filtered Master business list pagination |
| [sprint-14-registration-pagination.md](./sprint-14-registration-pagination.md) | Follow-on Sprint 14 — Master registration-request list pagination |
| [sprint-15-dashboard-kpi-filters.md](./sprint-15-dashboard-kpi-filters.md) | Follow-on Sprint 15 — Master dashboard KPI deep-links + account filter |
| [sprint-p8-1-architecture-audit-plan.md](./sprint-p8-1-architecture-audit-plan.md) | P8-1 sprint plan (completed) |

---

## Architecture & design notes

| Document | Description |
|----------|-------------|
| [architecture-audit-report.md](./architecture-audit-report.md) | Sprint 1 codebase audit |
| [database-relationships.md](./database-relationships.md) | FK / cascade / isolation (current) |
| [category-hierarchy.md](./category-hierarchy.md) | Parent/child categories |
| [07-database-design.md](./07-database-design.md) | Detailed table catalog (23 tables — current) |
| [08-database-erd.md](./08-database-erd.md) | Current ERD |
| [09-api-documentation.md](./09-api-documentation.md) | Extended API notes (partially historical examples) |
| [19-deployment.md](./19-deployment.md) | Legacy deploy notes — prefer [deployment-guide.md](./deployment-guide.md) |
| [`backend/sql/README.md`](../backend/sql/README.md) | SQL apply / inspect / stamp guide |

---

## Historical / hotel-era docs

Older numbered docs (`01`–`22`, `test-hotel-billing-guide.md`) describe the hotel MVP era. Use them for background only; **do not** treat hotel-only wording as product truth.

| Document | Status |
|----------|--------|
| [20-development-sprints.md](./20-development-sprints.md) | Superseded by [development-roadmap.md](./development-roadmap.md) |
| [22-saas-hotel-registration.md](./22-saas-hotel-registration.md) | Legacy registration notes; product path is **Register Business** |
| [test-hotel-billing-guide.md](./test-hotel-billing-guide.md) | Superseded by [test-business-billing-guide.md](./test-business-billing-guide.md) |

---

## Company

- **Legal:** Prabha Technology Pvt. Ltd.
- **Address:** B-05, First Floor, Shreya Business Hub, Pari Chowk, Mokarwadi, Pune, Maharashtra – 411041
- **Support:** prabha.technology.01@gmail.com · 8767865572
- **Plan (info only):** ₹550 / month — no in-app payment gateway; plans are now DB-managed via Master Admin (Phase 8)
