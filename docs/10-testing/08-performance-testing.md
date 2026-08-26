# Performance Testing

Master list pagination, KPI filters, index usage.

See [01-testing-strategy.md](./01-testing-strategy.md) and [../03-database/07-indexes-and-performance.md](../03-database/07-indexes-and-performance.md).

## POS search budget (BIZ-66)

| Metric | Target |
|--------|--------|
| Staging p95 | **≤ 200 ms** for barcode exact lookup and short-q POS catalog |
| CI light check | Catalog + barcode complete under **2 s** on SQLite test DB (not a staging substitute) |

### How to measure on staging

```powershell
# After login, time barcode + catalog (replace TOKEN / BASE)
Measure-Command {
  Invoke-RestMethod -Headers @{ Authorization = "Bearer $TOKEN" } `
    "$BASE/api/v1/items/by-barcode/YOUR_BARCODE"
}
Measure-Command {
  Invoke-RestMethod -Headers @{ Authorization = "Bearer $TOKEN" } `
    "$BASE/api/v1/grocery/pos/catalog?q=oil&limit=50"
}
```

Apply migration `20260826_biz66_perf_indexes` (or `python scripts/apply_perf_indexes.py`) before measuring.

### Automated

```powershell
cd backend
python -m pytest tests/test_biz66_performance_indexes.py -q
```
