# Book Stores — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-BOOK-001 | ISBN unique | Tenant type=bookstore; user logged in | Execute isbn unique | Per tenant | P0 |
| TEST-BOOK-002 | Sell by ISBN | Tenant type=bookstore; user logged in | Execute sell by isbn | Stock-- | P0 |
| TEST-BOOK-003 | Return | Tenant type=bookstore; user logged in | Execute return | Stock++ | P0 |
| TEST-BOOK-004 | Cross-tenant | Tenant type=bookstore; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-BOOK-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
