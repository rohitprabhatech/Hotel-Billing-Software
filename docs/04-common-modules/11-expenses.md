# Common Module — Expenses

**Status:** Implemented (BIZ-07)

Track daily business expenses with optional categories for P&L-style reporting.

## Capabilities

| Action | Owner | Manager | Billing User |
|--------|:-----:|:-------:|:------------:|
| List / view expenses | ✅ | ✅ | ❌ |
| Create expense | ✅ | ✅ | ❌ |
| Update expense | ✅ | ✅ | ❌ |
| Delete expense | ✅ | ✅ | ❌ |
| Expense summary report | ✅ | ✅ | ❌ |

Permissions: `expenses.read`, `expenses.write`.

## Data model

**expenses** — tenant-scoped entries:

| Field | Description |
|-------|-------------|
| `category` | Optional free-text label (e.g. Rent, Utilities) |
| `amount` | Positive decimal |
| `expense_date` | Calendar date (`YYYY-MM-DD`) |
| `notes` | Optional description |
| `created_by` | User who recorded the entry |

Categories are intentionally simple strings — no chart-of-accounts hierarchy in this sprint.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/expenses` | List with `q`, `category`, `from`, `to`, pagination |
| GET | `/api/v1/expenses/summary` | Total + breakdown by category for date range |
| POST | `/api/v1/expenses` | Create expense |
| GET | `/api/v1/expenses/:id` | Get one expense |
| PATCH | `/api/v1/expenses/:id` | Update expense |
| DELETE | `/api/v1/expenses/:id` | Delete expense |

Date filters use `from` / `to` query params (`YYYY-MM-DD`).

## Frontend

- Owner: `/owner/expenses`
- Manager: `/billing/expenses`

List view includes date-range filters, category/notes search, running total summary by category, and add/edit/delete form with category suggestions.

## Audit

`CREATE_EXPENSE`, `UPDATE_EXPENSE`, and `DELETE_EXPENSE` actions logged via audit service.

## Related

Future P&L reports can combine expense summary with sales reports (BIZ-61+).
