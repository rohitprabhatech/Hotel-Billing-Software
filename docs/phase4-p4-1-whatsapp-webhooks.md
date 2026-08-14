# Sprint P4-1 Completion Report — WhatsApp delivery webhooks

**Date:** 2026-08-14  
**Status:** **COMPLETED**  
**Phase:** 4 (post Phase 3 gate)

---

## Implementation

- `bill_deliveries` statuses: `PENDING | SENT | DELIVERED | READ | FAILED`
- Columns `delivered_at`, `read_at`; index on `provider_message_id`
- Public endpoints:
  - `GET /api/v1/webhooks/whatsapp` — Meta hub verify
  - `POST /api/v1/webhooks/whatsapp` — HMAC `X-Hub-Signature-256` with `WHATSAPP_APP_SECRET`
- Maps Meta `sent/delivered/read/failed` onto existing rows by `provider_message_id`
- No status downgrade (e.g. READ cannot become SENT); FAILED only from PENDING/SENT
- Bills history chips: Sent / Delivered / Read / Failed / Pending

## Ops

```text
python scripts/apply_pending_schema.py
```

Env:

- `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
- `WHATSAPP_APP_SECRET`
- Callback URL: `https://<host>/api/v1/webhooks/whatsapp`

In mock/dev without app secret, POST signatures are accepted only when `WHATSAPP_PROVIDER=mock`.

## Testing

```text
pytest tests/test_p4_1_whatsapp_webhooks.py tests/test_p3_3_whatsapp_bill_delivery.py -q
→ passed
npm run build → OK
```

## Documentation

- This report + plan; roadmap Phase 4 row; API + owner manual webhook notes

## Known issues

- Webhook does not create bills or send messages — status only
- Requires public HTTPS URL for live Meta

---

**Stopped.** Should I start the next sprint?
