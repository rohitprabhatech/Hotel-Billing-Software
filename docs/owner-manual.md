# Owner Manual — Business Billing

For users with role **OWNER**.

## Console map

| Menu | Purpose |
|------|---------|
| Dashboard | Business name/type, period KPIs, recent activity |
| Billing | Opens the counter workspace (same tools as Billing Users) |
| Bills | Searchable bill history, view, print, WhatsApp send/retry, cancel |
| Items | Catalog: price, GST, SKU, cost, stock; soft deactivate |
| Item Activity | Who created/edited/deactivated items |
| Categories | Main + subcategories (parent picker); soft deactivate |
| Sales Reports | Daily / weekly / monthly / custom + export |
| AI Assistant | Tenant-scoped analysis & decision support (no invented numbers) |
| Audit & Activity | Login, bills, password changes, WhatsApp sends, etc. |
| Users | Invite Billing Users; reset passwords |
| Settings | Profile, business info, **WhatsApp integration**, subscription info, appearance, email |
| Profile | Personal name / phone / email change |

## First-week checklist

1. **Settings → Business Information** — confirm name, type, GST, bill prefix, address.  
2. **Settings → WhatsApp Business Integration** (optional) — Phone Number ID, WABA ID, access token, approved template name; Test Connection. Token is never shown again after save.  

   **Live Meta checklist:** create a WhatsApp Cloud API app → add a phone number → create/approve a **document** template (business name, bill number, amount) → set `WHATSAPP_PROVIDER=meta` and a strong `WHATSAPP_TOKEN_ENCRYPTION_KEY` on the server → paste Phone Number ID, WABA ID, token, and exact template name in Settings. Use `mock` for local testing without Meta.

   **Webhooks (delivery status):** in Meta App → WhatsApp → Configuration, set Callback URL to `https://<your-api-host>/api/v1/webhooks/whatsapp`, use the same Verify Token as `WHATSAPP_WEBHOOK_VERIFY_TOKEN`, and set `WHATSAPP_APP_SECRET` to the Meta App Secret. Subscribe to **messages** field so status updates (`delivered` / `read` / `failed`) update bill delivery chips in Bills history.

   In **mock** mode, Settings shows a **Mock delivery webhook simulator** so you can paste a provider message id from a sent bill and advance status (including failed with a reason) without Meta. Bills history can filter by WhatsApp status and shows failure reasons / delivery timestamps.  
3. Add **Categories** — leave Parent as **No Parent / Main Category** for mains, then add subcategories.  
4. Add **Items** with price + GST (SKU/stock optional).  
5. Create a **Billing User** under Users.  
6. Run a test bill (Cash and Online); try **Print** and **Send on WhatsApp** if configured.  
7. Open **Reports** and export a sample CSV/PDF.  
8. Try **AI Assistant** after a few sales exist.  
9. Note **Subscription** (₹550/mo info) — contact Prabha Technology to subscribe; no checkout in app.  
10. Set **Appearance** (light/dark) if desired.

## Practice sample (grocery)

Use these **exact** entries for a first dry-run (full checklist: [test-business-billing-guide.md](./test-business-billing-guide.md) Script G).

| What | Exact value |
|------|-------------|
| Business | `Shree General Store` · Grocery Store |
| Owner | `Rajesh Patil` · `owner@example.com` · `Owner@12345` |
| Billing User | `Amit Sharma` · `billing@example.com` · `Billing@12345` |
| Categories | Grocery → Rice, Pulses; Beverages → Cold Drinks |
| Items (5% GST) | Rice 5kg ₹450; Dal 1kg ₹140; Cold Drink 750ml ₹50; Biscuits ₹30 |
| Cash bill | Rice + Dal, Reference `C-1` → grand **₹620** |
| Online bill | Cold Drink ×2; add then **remove** Biscuits before finalize, Reference `C-2` → grand **₹105** |

## Reports & AI

- Reports stay scoped to **your** business only.  
- AI uses recorded bills only; empty periods show **insufficient data**.  
- Decision support lists best/slow movers and recommendations from history — not fabricated forecasts.

## Security habits

- Prefer unique Billing User accounts (don’t share Owner login).  
- Change password regularly; changing password signs out other sessions.  
- Suspend access by deactivating a user rather than sharing passwords.

## Support

prabha.technology.01@gmail.com · 8767865572  
B-05, First Floor, Shreya Business Hub, Pari Chowk, Mokarwadi, Pune, Maharashtra – 411041
