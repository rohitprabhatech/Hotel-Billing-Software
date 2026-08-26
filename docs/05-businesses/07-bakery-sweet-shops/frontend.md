# Bakery / Sweet Shops — Frontend

| Page | Route | Roles | Module | Status |
|------|-------|-------|--------|--------|
| Custom Cake Orders | `/owner/cake-orders` | Owner / Manager / Billing (create+advance) | `custom_orders` | BIZ-42 |
| Production | `/owner/production` | Owner / Manager | `production` | BIZ-40 (+ expiry on FG batches in BIZ-41) |
| Batches / Expiry | `/owner/batches` | Owner / Manager | `batch_expiry` | Shared BIZ-22 / bakery BIZ-41 |
| Recipes | `/owner/recipes` | Owner / Manager | `recipe` | Shared (BIZ-16) |
| Wastage | `/owner/wastage` | Owner / Manager | `wastage` | Shared (BIZ-18 / BIZ-41) |
| New Bill / Items | common | Owner / Manager / Billing | — | FEFO blocks expired FG when policy on |


## Shared UI

Reuse common Billing, Customers, Reports pages. Industry nav items appear only when the module is enabled (`OwnerLayout` + `useModuleGate`).

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
