# Testing Guide — Prabha Billing SaaS V2

**Phase:** Testing **architecture** and templates. Do not run destructive tests against production data.

Existing E2E detail: [test-business-billing-guide.md](./test-business-billing-guide.md).

---

## 1. Test layers

| Layer | Tooling |
|-------|---------|
| Backend unit/API | `pytest` + venv · `FLASK_ENV=testing` |
| Frontend build | `npm run build` |
| Manual UAT | Scripts in test-business-billing-guide |
| Isolation | Tenant A vs B cross-access |
| Security | Authz, secrets, rate limits |
| Regression | Full pytest before sprint close |

## 2. Case template

```
Test ID:
Module:
Precondition:
Test Data:
Steps:
Expected Result:
Actual Result:
Status: Pass / Fail / Blocked
```

## 3. Mandatory suites (build over sprints)

| Suite | Covers |
|-------|--------|
| T-REG | Registration pending / approve / reject |
| T-AUTH | Valid/invalid login, tokens, logout, master path |
| T-ISO | Cross-tenant 403/404 on all new resources |
| T-BILL | Create bill, stock check, pay, cancel, print, PDF, WhatsApp |
| T-INV | Receive, adjust, insufficient stock, concurrency |
| T-CRM | Customers/suppliers CRUD (when built) |
| T-SUB | Trial, expiring, expired lockout, plan visibility |
| T-MAS | Master approve, plans, deactivate, audit |
| T-AI | Tenant-scoped insights only |
| T-UI | Responsive, dark mode, Owner↔Billing navigation |
| T-IND-* | Per industry pack smoke tests |

## 4. Isolation checklist

Users · Customers · Products · Categories · Bills · Payments · Purchases · Inventory · Expenses · Reports · Notifications · Audit · Settings · Subscription views.

## 5. Definition of done (per sprint)

- New tests green  
- No production data deleted  
- Docs updated for changed behavior  
- Acceptance criteria checked  

## 6. Explicit non-tests

Medical Store scenarios — **out of scope**.
