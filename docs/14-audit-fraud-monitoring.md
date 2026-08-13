# 14 — Audit & Fraud Monitoring

## Purpose

Give the Hotel Owner visibility into Billing User (and all user) actions without auto-accusing anyone of fraud. Present **Activity**, **Alerts**, and **Audit Events** for investigation.

## Audit Log Record

| Field | Description |
|-------|-------------|
| tenant_id | Isolation key |
| user_id | Actor |
| user_name | Display snapshot |
| action | Enumerated action code |
| entity_type | BILL, ITEM, CATEGORY, USER, AUTH, REPORT, TENANT |
| entity_id | Target id |
| old_data | JSON before |
| new_data | JSON after |
| ip_address | When available |
| user_agent | When available |
| created_at | Timestamp |

## Action Catalog

```text
LOGIN
LOGOUT

CREATE_ITEM
UPDATE_ITEM
DEACTIVATE_ITEM
UPDATE_PRICE
CHANGE_GST

CREATE_CATEGORY
UPDATE_CATEGORY
DEACTIVATE_CATEGORY

CREATE_BILL
UPDATE_DRAFT_BILL
CANCEL_BILL
VOID_BILL
ADD_BILL_ITEM
REMOVE_BILL_ITEM

PRINT_BILL
REPRINT_BILL

CREATE_USER
UPDATE_USER
DEACTIVATE_USER

UPDATE_TENANT
EXPORT_REPORT
CHANGE_GST_CONFIG
```

## Immutability

- No API to delete or edit audit logs
- Application users cannot purge history
- Append-only inserts from service layer

## Owner Audit Dashboard

Filters:

- User
- Action
- Date range
- Bill number
- Item
- Entity type

Table example:

```text
Date              User           Action          Bill
13-Aug-2026       Billing User   CREATE_BILL     INV-105
13-Aug-2026       Billing User   CANCEL_BILL     INV-107
13-Aug-2026       Billing User   REPRINT_BILL    INV-105
```

### Detail Panel

For `CANCEL_BILL`:

- Who cancelled
- When
- Bill number
- Reason
- Original amount
- Status transition

## Activity Alerts (Indicators)

Compute heuristics (configurable thresholds later):

| Indicator | Example signal |
|-----------|----------------|
| High cancellations | Cancel count today > N |
| Same user cancellations | User cancel count > N in period |
| Unusual discounts | Discount % or amount above threshold |
| Frequent reprints | `printed_count` or REPRINT events > N |
| Price changes | UPDATE_PRICE events in period |
| Deactivated items | DEACTIVATE_ITEM count |
| Login activity | Failed/success logins (if tracked) |

Display as **Activity Alerts**, not guilt labels.

## Integration Points

| Event | When to write audit |
|-------|---------------------|
| Auth | After login success / logout |
| Item/price/GST | Same transaction as change |
| Bill create | Same transaction as finalize |
| Cancel | Same transaction as status update |
| Print | After successful print notification |
| Export | When export generated |

Prefer **same DB transaction** for financial mutations + audit so logs cannot diverge from facts.

## Permissions

- OWNER: list, detail, alerts
- BILLING_USER: none
- Cross-tenant: impossible by design

## Acceptance Criteria

- Cancelled bill shows actor, reason, amount in audit detail
- Billing User actions appear for owner filters
- No delete audit endpoint
- Alerts surface high cancellation / reprint patterns without false legal claims
