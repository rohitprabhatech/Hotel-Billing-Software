# Common Module — Payments

Distinguish:

1. **Customer payments** on bills (cash / online / credit / partial collection)
2. **SaaS subscription payments** to Prabha (often offline/manual)

Do not mix ledgers.

## Bill payment methods (BIZ-09 extended)

| Method | Code | Behavior |
|--------|------|----------|
| Cash | `cash` | Immediate cash sale |
| Online | `online` | UPI/card/online settlement |
| Credit | `credit` | Udhari — requires linked `customer_id`; increases customer balance |

Credit bills do **not** count as cash/online in payment-filtered sales reports.

## Party ledger (customer credit)

**party_ledger_entries** — tenant-scoped running ledger:

| Field | Purpose |
|-------|---------|
| `party_type` | `CUSTOMER` (supplier later) |
| `party_id` | Customer id |
| `entry_type` | `CREDIT_SALE`, `PAYMENT`, `BILL_CANCEL` |
| `amount` | Signed — positive increases balance owed, negative decreases |
| `balance_after` | Snapshot after entry |
| `reference_type` / `reference_id` | Link to bill or payment |

**customers.balance** — cached outstanding amount updated atomically with ledger writes.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/customers/:id/ledger` | Ledger entries + current balance |
| POST | `/api/v1/customers/:id/payments` | Collect partial/full payment (`amount`, `collection_method`, `notes`) |
| GET | `/api/v1/customers/outstanding` | Customers with balance &gt; 0 |

## Rules

- Credit bill requires active customer; optional `credit_limit` enforced on new balance
- Payments cannot exceed outstanding balance (no silent negative balance)
- Cancelling a credit bill posts `BILL_CANCEL` reversal
- Owner, Manager, and Billing User may collect payments (`customers.write`)

## Frontend

- **Customers page:** balance badge, outstanding filter, ledger view, collect payment dialog
- **New Bill:** Credit (Udhari) option when a customer is linked

## Audit

`CREDIT_SALE`, `COLLECT_CREDIT_PAYMENT`, `CREDIT_BILL_CANCEL` logged via audit service.
