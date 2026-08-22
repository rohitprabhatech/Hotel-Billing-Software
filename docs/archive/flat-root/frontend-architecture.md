# Frontend Architecture — Prabha Billing SaaS V2

**Stack:** React · Vite · MUI · Axios  
**Phase:** Documentation only

---

## 1. Current structure (retain)

```
frontend/src/
  components/ layouts/ pages/ routes/ services/
  context/ hooks/ theme/ constants/ utils/
```

Layouts: `AuthLayout`, `OwnerLayout`, `BillingLayout`, `MasterLayout`.  
Paths centralized in `routes/paths.js`.

---

## 2. Target module layout (conceptual)

```
frontend/src/
  ...existing...
  modules/
    billing/
    inventory/
    customers/
    restaurant/
    cafe/
    grocery/
    clothing/
    mobile/
    hardware/
    bakery/
    stationery/
    electronics/
    furniture/
    building-material/
    books/
    wholesale/
    travel/
```

Each module: pages, local components, hooks. Shared UI stays in `components/`.

---

## 3. Routing principles

| Concern | Approach |
|---------|----------|
| Auth | `ProtectedRoute` + role home path |
| Feature flags | Hide nav items when module disabled |
| Master | `/master/*` isolated; footer-dot entry |
| Industry | Lazy-loaded routes registered from config |

---

## 4. Known UX debt (document only)

Owner → Billing switches layouts; return via **Owner Dashboard** only. Dual Dashboard labels. Fix in UI/UX sprint — not now.

---

## 5. UX standards

- Professional SaaS look; consistent spacing/typography  
- Avoid excessive cards/gradients/oversized CTAs  
- Loading / empty / error states on every list  
- Dark mode support (existing theme)  
- Mobile responsive grids  

---

## 6. API client

Axios instance with JWT; 401 logout; 402 subscription lockout UI. Never send `tenant_id` for authorization.
