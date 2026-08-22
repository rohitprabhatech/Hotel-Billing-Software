# Book Stores — Frontend

Conceptual routes under `modules/books/` (not implemented yet).

| Page | Purpose | Roles | Components | API deps | UX |
|------|---------|-------|------------|----------|-----|
| Bookstore Dashboard | Book Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Catalog (ISBN) | Book Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| POS Billing | Book Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Returns | Book Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |
| Reports | Book Stores ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |

## Shared UI

Reuse common Billing, Customers, Reports pages. Industry nav items appear only when the module is enabled.

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
