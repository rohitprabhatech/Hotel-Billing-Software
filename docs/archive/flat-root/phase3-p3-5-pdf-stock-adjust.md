# Sprint P3-5 Completion Report — Bill PDF + stock adjust

**Date:** 2026-08-14  
**Status:** **COMPLETED**

---

## Implementation

### Bill PDF download
- `GET /api/v1/bills/:id/pdf` — same `BillPdfService` used for WhatsApp (saved bill totals)
- FE: **Download PDF** on New Bill success dialog and bill history detail
- Thermal **Print Bill** unchanged (`window.print`)

### Stock adjust
- `POST /api/v1/items/:id/adjust-stock` `{ delta, reason? }`
- Row lock via `lock_by_id_and_tenant`; rejects untracked (null) stock and negative result
- Audit `STOCK_ADJUSTED`; stock alert recovery via existing notify transition
- Items page inventory icon → Adjust Stock dialog

### ErrorBoundary
- Auth layout pages + `/print/bills/:id` wrapped

### Concurrent stock note
- Billing create/cancel already use `FOR UPDATE` locks; SQLite test env cannot prove races. Production MySQL relies on those locks. No code gap found in lock path.

## Testing

```text
pytest tests/test_p3_5_pdf_stock_adjust.py -q
→ 3 passed
npm run build → OK
```

## Docs
- Plan + this report; roadmap P3-5; API map updated

## Known issues
- Meta WhatsApp webhooks still deferred
- Full MySQL concurrent stress harness not automated in CI (SQLite)

---

**Stopped.** Should I start the next sprint?
