# Billing User Manual — Business Billing

For users with role **BILLING_USER**.

## What you can do

- Open **Billing Dashboard** (today’s counts and recent bills)  
- Create **New Bill**, print, **Send on WhatsApp**, and cancel (with reason)  
- Browse **Today’s Bills** / bill history (includes WhatsApp delivery status)  
- Add and edit **Items** (soft deactivate when needed)  
- Browse **Categories** (read-only; Owners manage structure)  
- Update **Profile** and **Change Password**  
- Toggle **Light / Dark** mode  

You cannot open Owner-only areas: Reports, AI, Audit, Users, or business Settings (including WhatsApp configuration).

## New Bill (counter flow)

1. Go to **New Bill**.  
2. Search by name/SKU; filter by category chips if needed.  
3. Add lines; change quantity — set qty to **0** or use remove to drop a line.  
4. Optional **discount**.  
5. Enter **Reference** (table number, token, bag note — whatever your shop uses).  
6. Optional **customer name** and **mobile** (country code + number) — required only if you will send WhatsApp.  
7. Select **Cash** or **Online**.  
8. Generate bill → **Print Bill**, **Download PDF**, and/or **Send on WhatsApp** (independent).  

If WhatsApp is not configured by the Owner, you will see a clear message to contact them. Failed sends can be **retried** without creating another bill.

If the business subscription is expired, cancelled, or billing-suspended, New Bill and catalog APIs are locked (payment required). You can still sign in and open Profile. Ask the Owner to contact Prabha Technology.

**Stock:** On Items, use the inventory icon to **Adjust stock** (+/−) with an optional reason — do not recreate the bill.

Receipts keep historical item names and prices even if the catalog changes later.

## Practice sample (grocery counter)

If your Owner set up **Shree General Store** sample catalog:

| Bill | Exact cart | Payment | Reference | Expected grand |
|------|------------|---------|-----------|----------------|
| 1 | `Rice 5kg` ×1 + `Dal 1kg` ×1 | Cash | `C-1` | **₹620** |
| 2 | `Cold Drink 750ml` ×2 + `Biscuits` ×1, then **remove Biscuits** | Online | `C-2` | **₹105** |

Removing Biscuits from the cart does **not** delete it from the Items catalog.

## Tips

- Prefer searching by SKU for dense catalogs.  
- If an item is missing, create it under **Items** (or ask the Owner).  
- Cancel only when necessary; cancellations are audited.  
- After a password change you must sign in again.

## Support

Ask your business Owner first; provider support: prabha.technology.01@gmail.com · 8767865572
