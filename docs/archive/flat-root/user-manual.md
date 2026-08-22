# User Manual — Prabha Billing SaaS / Business Billing

**Provider:** Prabha Technology Pvt. Ltd.  
**Support:** 8767865572 · prabha.technology.01@gmail.com · 24/7  
**Status:** Structure + current workflows. Industry-specific chapters expand as modules ship.

> Medical Stores are **not** supported. Do not document pharmacy workflows.

---

## 1. What it is

Cloud multi-tenant billing and business management for **14** shop types (restaurant, cafe, grocery, clothing, mobile, hardware, bakery, stationery, electronics, furniture, building material, books, wholesale, travel). Each business is an isolated **tenant**.

## 2. Roles

| Role | Focus |
|------|--------|
| Owner | Catalog policy, users, reports, AI, audit, settings, billing |
| Billing User | Counter billing, items (if permitted), bill history |
| Manager | Target mid-tier role (future) |
| Master Admin | Prabha Technology only — approvals, plans, trials, lifecycle |

## 3. Register & approve

1. Landing → **Register Your Business** → select **business type** → accept Terms/Privacy.  
2. Wait for Master **approval** (pending = no login).  
3. Sign in at `/login`.  
4. Trial (if enabled) or wait for plan assignment.

Master: footer **dot** → `/master/login`. See [master-admin-manual.md](./master-admin-manual.md).

## 4. Common workflows (available today)

| Goal | Where |
|------|--------|
| Create a sale | Billing → New Bill |
| Bill history / reprint / PDF / WhatsApp | Bills |
| Catalog | Items / Categories |
| Stock receive / adjust | Items + Stock Movements |
| Reports | Owner → Sales Reports |
| AI | Owner → AI Assistant |
| Users / audit / settings | Owner console |
| WhatsApp config | Owner → Settings |

## 5. Planned industry workflows (future manuals)

Document when modules ship: Tables/KOT (restaurant) · Credit/udhari (grocery/wholesale) · Size/color (clothing) · IMEI (mobile) · Bookings (travel) · etc. See [industry-modules.md](./industry-modules.md).

## 6. Subscription

Landing prices from plan catalog. In-app **no Pay button** — contact Prabha Technology to activate/renew. Owner Settings shows entitlement.

## 7. Known UX note

From Owner, opening Billing switches to the Billing shell. Return via **Owner Dashboard** in the Billing menu (documented issue; fix planned in UX sprint).

## 8. Related

[owner-manual.md](./owner-manual.md) · [billing-user-manual.md](./billing-user-manual.md) · [testing-guide.md](./testing-guide.md)
