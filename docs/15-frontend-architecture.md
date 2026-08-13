# 15 — Frontend Architecture

## Stack

- React.js
- Material UI (MUI)
- React Router
- Axios
- Responsive layout

## Folder Structure

```text
frontend/
├── public/
├── src/
│   ├── components/          # Shared UI (tables, confirm dialogs, loaders)
│   ├── layouts/             # OwnerLayout, BillingLayout, AuthLayout
│   ├── pages/
│   │   ├── auth/
│   │   ├── owner/           # Dashboard, reports, audit, users, settings
│   │   ├── billing/         # Billing home, new bill, recent bills
│   │   ├── items/
│   │   ├── categories/
│   │   ├── bills/
│   │   └── reports/
│   ├── services/            # Axios API modules
│   ├── hooks/
│   ├── context/             # AuthContext
│   ├── routes/              # Route config + guards
│   ├── utils/
│   ├── theme/               # MUI theme (professional, not gaming)
│   ├── print/               # BillPreview, PrintableReceipt
│   └── App.jsx
├── package.json
└── .env.example
```

## Route Trees

```text
/login
/owner/dashboard
/owner/categories
/owner/items
/owner/bills
/owner/reports
/owner/audit
/owner/users
/owner/settings
/billing
/billing/new
/billing/bills
/print/bills/:id
```

## Role-Based UX

| Role | Primary experience |
|------|--------------------|
| OWNER | Analytics cards, tables, charts, audit, exports |
| BILLING_USER | Fast billing screen; today's bills/total; recent bills |

Do not overload Billing User with owner analytics.

## State & Data

- AuthContext: token, user, role, tenant summary
- Server state via Axios services; avoid over-engineering global stores in v1
- Cart state local to New Bill page until finalize

## API Client

- Base URL from env
- Request interceptor: attach JWT
- Response interceptor: 401 → logout/redirect
- Never send `tenant_id` for authorization

## UI Standards

- Clean, professional MUI
- Consistent typography, spacing, buttons, tables, dialogs
- Loading / empty / error states
- Confirmation dialogs for cancel bill & deactivate item
- Desktop-first billing ergonomics

## Print Isolation

`PrintableReceipt` rendered on print route with print CSS; hide app shell.

## Environment

```text
REACT_APP_API_BASE_URL=http://localhost:5000/api/v1
```
