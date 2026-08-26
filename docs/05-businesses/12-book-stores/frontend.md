# Book Stores — Frontend

| Page | Path | Roles | Notes |
|------|------|-------|-------|
| Books catalog (Items) | `/owner/items`, `/billing/items` | Owner / Manager / Billing | ISBN / Author / Publisher when `book_metadata` on |
| Grocery / barcode POS | `/owner/grocery`, `/billing/grocery` | As permitted | Shared POS; catalog search includes ISBN/author |
| Returns | `/owner/returns` | As permitted | Module `returns_exchange` |

## UX (BIZ-45)

- Items search label becomes “Search name, ISBN, author…” for book stores.
- Create/edit form shows ISBN, Author, Publisher fields.
- List subtitle shows author · ISBN · publisher.

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
