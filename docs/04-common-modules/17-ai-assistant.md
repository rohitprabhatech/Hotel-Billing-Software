# Common Module — AI Assistant

Tenant-scoped insights only; no invented metrics; industry-aware analyzers as modules exist. Never cross-tenant. **Deterministic / rule-based** — not an LLM.

## Analysis API

`GET /api/v1/ai/analysis` (Owner) returns core sales analysis plus optional `industry_insights`.

`analysis_mode` is always `"rule_based"`.

## Industry plugin pattern (BIZ-62)

Source: `backend/app/services/ai_industry_analyzers.py`

1. Implement `AnalyzerFn(tenant_id, start, end, label) -> dict | None`
2. Register in `INDUSTRY_ANALYZERS` with the module code(s) that must be enabled
3. Return insights with `based_on` citations of real aggregates only

| Module | Analyzer | Notes |
|--------|----------|-------|
| `order_channels` | F&B channel / table / wastage | Restaurant & cafe |
| `serial_imei` | In-stock + 90-day aging | Mobile / electronics |
| `customer_credit` | Outstanding balances | Grocery, wholesale, etc. |
| `travel_commission` | Pending / top agent | Travel |

Restaurant tenants see **F&B insights only** among industry plugins (plus core sales) — never clothing/IMEI/travel packs.
