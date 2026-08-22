# Electronics Shops — Frontend

Conceptual routes under `modules/electronics/` (not implemented yet).

| Page | Purpose | Roles | Components | API deps | UX |
|------|---------|-------|------------|----------|-----|
| Electronics Dashboard | Electronics Shops ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Serial Stock | Electronics Shops ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Billing | Electronics Shops ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Warranty / Repair / Install | Electronics Shops ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Returns | Electronics Shops ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Reports | Electronics Shops ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |

## Shared UI

Reuse common Billing, Customers, Reports pages. Industry nav items appear only when the module is enabled.

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
