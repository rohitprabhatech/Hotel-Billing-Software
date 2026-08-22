# Product Requirements — Prabha Billing SaaS V2

**Status:** Draft for review · Documentation phase  
**Must not:** change code or database until approval

---

## 1. Goals

1. One multi-tenant SaaS for **14** business types.  
2. Common Core + Industry Modules.  
3. Master-controlled registration, trial, plans, activation.  
4. Strict tenant isolation.  
5. Extend existing Business Billing foundation.  
6. Exclude Medical Stores entirely.

---

## 2. Stakeholders

| Stakeholder | Need |
|-------------|------|
| Prabha Technology | Master ops, subscriptions, audit |
| Business Owner | Configure, oversee, reports |
| Staff (Billing / Manager) | Daily operations within permissions |
| End customers of shops | Receive invoices / WhatsApp (indirect) |

---

## 3. Functional themes

| ID | Theme | Priority |
|----|-------|----------|
| PR-01 | Auth + RBAC + Master auth | P0 (exists → harden) |
| PR-02 | Registration approval | P0 (exists) |
| PR-03 | Business type → module matrix | P0 (new) |
| PR-04 | Shared billing engine (product/service) | P0 (extend) |
| PR-05 | Flexible inventory engine | P0 (extend) |
| PR-06 | Customers / suppliers / purchase / expense | P1 |
| PR-07 | Industry packs (14) | P1–P2 phased |
| PR-08 | Industry dashboards | P1 |
| PR-09 | Reports + export | P1 (extend) |
| PR-10 | Notifications + audit | P0 (extend) |
| PR-11 | Subscription + trial + limits | P0 (extend) |
| PR-12 | AI assistant (generic) | P2 (exists → broaden) |
| PR-13 | WhatsApp / print / PDF | P1 (exists → broaden) |
| PR-14 | Landing + dynamic pricing | P0 (exists → 14 industries) |
| PR-15 | UX professionalization | P1 |
| PR-16 | Security / backup / privacy docs | P0 |

---

## 4. Non-functional

| Area | Requirement |
|------|-------------|
| Isolation | Backend resolves tenant from JWT only |
| Concurrency | Stock checks prevent negative stock (unless setting) |
| Performance | Paginated lists; indexed tenant queries |
| Availability | Cloud SaaS; backup/restore documented |
| UX | Responsive, dark mode, consistent MUI |
| Secrets | Never commit credentials |

---

## 5. Explicit exclusions

- Medical Store / pharmacy / prescription / medicine batch modules  
- Dropping production tables without approval  
- Trusting `tenant_id` from frontend payloads  

---

## 6. Success criteria (product)

- New business picks one of 14 types and receives correct module set.  
- Core billing works for product, service, and mixed invoices.  
- Master can configure trial/plans without code deploy.  
- Tenant A never reads Tenant B data.  
- Medical Store never appears in UI, docs, or schema plans.
