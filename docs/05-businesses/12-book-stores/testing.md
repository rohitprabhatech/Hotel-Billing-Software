# Book Stores — Testing

## Automated (BIZ-45)

Suite: `backend/tests/test_biz45_book_store_metadata.py` (5 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_book_store_module_flags` | book_metadata + barcode/bulk/returns |
| `test_book_metadata_fields_and_update` | create/update ISBN/author/publisher |
| `test_isbn_unique_per_tenant` | 409 on duplicate (hyphen-normalized) |
| `test_search_by_isbn_author_and_books_api` | `q`, `isbn`, `/books/catalog`, `/books/by-isbn` |
| `test_books_forbidden_without_module` | restaurant → 403 |

## Automated (Phase 08 gate — BIZ-46)

Book returns / exchange + combined gate in `test_biz46_stationery_books_testing_gate.py`. Full Phase 08 — **20 passed** (2026-08-26). See [biz-46-stationery-books-gate-report.md](../../14-sprints/biz-46-stationery-books-gate-report.md).

## Manual smoke

| Test ID | Purpose | Expected | Priority |
|---------|---------|----------|----------|
| TEST-BOOK-001 | Create book with ISBN | Saved; duplicate ISBN blocked | P0 |
| TEST-BOOK-002 | Search by author / ISBN on Items | Hits appear | P0 |
| TEST-BOOK-003 | Sell via barcode POS after ISBN search | Stock ↓ | P0 |
| TEST-BOOK-004 | Return sold book | Stock ↑ + refund | P0 |
| TEST-BOOK-005 | Exchange for another title | Sold restocked; swap deducted | P0 |

Do not run destructive tests on production data.
