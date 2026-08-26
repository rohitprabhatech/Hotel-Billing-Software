# Book Stores — API

Book metadata lives on common `/items`. Thin aliases under `/api/v1/books/...` (module `book_metadata`).

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST/PUT | `/api/v1/items` (+ `/:id`) | Catalog CRUD including `isbn`, `author`, `publisher` | JWT | items read/write | Yes |
| GET | `/api/v1/items?q=` | Search name/SKU/barcode/**ISBN/author/publisher** | JWT | items:read | Yes |
| GET | `/api/v1/items?isbn=` | Exact ISBN (hyphens optional) | JWT | items:read | Yes |
| GET | `/api/v1/books/catalog` | Alias of items list (requires `book_metadata`) | JWT | items:read | Yes |
| GET | `/api/v1/books/by-isbn/{isbn}` | Exact ISBN lookup | JWT | items:read | Yes |

Returns / barcode POS reuse common + grocery endpoints (modules already on `book_store`).

## Contract notes

- **ISBN uniqueness:** per tenant; 409 on duplicate.
- **Normalization:** hyphens and spaces stripped on write/lookup.
- **Errors:** 401 / 403 (missing module) / 404 / 409.

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
