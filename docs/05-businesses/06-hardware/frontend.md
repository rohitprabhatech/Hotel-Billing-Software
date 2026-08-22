# Hardware Stores — Frontend

Conceptual routes under `modules/hardware/` (not implemented yet).

| Page | Purpose | Roles | Components | API deps | UX |
|------|---------|-------|------------|----------|-----|
| Hardware Dashboard | Hardware Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Products / Units | Hardware Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Billing | Hardware Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Credit | Hardware Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Price History | Hardware Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Reports | Hardware Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |

## Shared UI

Reuse common Billing, Customers, Reports pages. Industry nav items appear only when the module is enabled.

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
