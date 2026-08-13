# 13 — Sales Reporting

## Audience

**Hotel Owner only.** Billing User has a minimal today-total on their dashboard, not full analytics.

## Dashboard Cards (Today)

| Metric | Definition |
|--------|------------|
| Today's Sales | Sum of `grand_total` for FINALIZED bills today (exclude CANCELLED/VOID or define clearly) |
| Today's Bills | Count of finalized bills today |
| Today's Discount | Sum of discounts |
| Today's GST | Sum of `gst_amount` |
| Average Bill | Sales / bill count |
| Items Sold | Sum of quantities from bill_items |
| Cancelled Bills | Count of cancellations today |

**Policy:** Cancelled bills are excluded from sales totals but counted in cancelled metrics. Document in UI tooltips.

## Period Filters

- Today
- Yesterday
- This Week
- This Month
- Last Month
- Custom Date Range (`from`, `to`, inclusive in tenant timezone or UTC—pick one and document)

## Comparisons

Owner UI shows side-by-side examples:

```text
Today's Sales       vs  Yesterday's Sales
This Month          vs  Last Month
```

API may return `current` and `previous` blocks from `/reports/summary`.

## Report Contents

### Daily / Period Summary

- Total sales
- Bill count
- Total discount
- Total GST
- Average bill
- Cancelled count

### Monthly / Custom Add-ons

- **Item-wise sales** — item_name snapshot, qty, revenue
- **Day-wise sales** — date, sales, bills

## Export

| Format | Use |
|--------|-----|
| Excel `.xlsx` | Primary owner export |
| CSV | Lightweight |
| PDF | Summary where appropriate |

### Rules

- Tenant-scoped data only
- Filename pattern: `{BusinessName}_{Period}_Sales.xlsx` (sanitize)
- Audit: `EXPORT_REPORT` with period/format metadata
- No cross-tenant rows

## API Mapping

| UI | API |
|----|-----|
| Dashboard cards + comparisons | `GET /reports/summary` |
| Daily | `GET /reports/daily-sales` |
| Monthly | `GET /reports/monthly-sales` |
| Custom | `GET /reports/custom-sales` |
| Export | `GET /reports/export` |

## Charts (Owner UI)

- Day-wise sales bar/line for month/custom
- Optional item top-N chart

Use MUI + a lightweight chart library (chosen in Sprint 7). Keep professional, not gaming-style.

## Timezone

Store UTC in DB; for "today" boundaries use tenant-configured timezone (default `Asia/Kolkata` for Indian hotels) in reporting service.
