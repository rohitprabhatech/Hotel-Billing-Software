# Database / relationship + speed pass (2026-08-16)

**Goal:** Align live DB indexes with hot paths and stop bill list from loading every line item.

## Changes

| Area | Before | After |
|------|--------|-------|
| `Bill.items` ORM | `lazy="joined"` (every bill query JOINed all lines) | `lazy="selectin"`; list uses `noload(items)` |
| Bill list `count()` | Wrapped full ORM SELECT subquery | `count(distinct Bill.id)` |
| Delivery status on list | Two queries (WA + email) | One batched query |
| Indexes | Missing method/created composites on deliveries/stock | `ix_bill_deliveries_tenant_method_bill_created`, `ix_stock_movements_tenant_item_created` |
| Docs | Relationships map pre-delivery/stock | Updated `database-relationships.md` |

## Ops

```text
cd backend
# with DATABASE_URL / .env
python -c "from dotenv import load_dotenv; load_dotenv(); import runpy; raise SystemExit(runpy.run_path('scripts/apply_pending_schema.py')['main']())"
```

Or only: `scripts/apply_perf_indexes.py`.

## Verify

```text
pytest tests/test_bill_list_performance.py tests/test_item_list_performance.py -q
```
