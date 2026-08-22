# Trial Management — Business Billing

**Product:** Business Billing · Prabha Technology Pvt. Ltd.  
**Operator UI:** Master → Trial settings, Trials, Businesses

---

## Global defaults

Singleton `platform_settings`:

| Field | Typical default | Applies to |
|-------|-----------------|------------|
| `trial_enabled` | true | **New approvals only** |
| `trial_days` | 15 | New approvals only |
| `expiry_warning_days` | 5 | Warning banners / EXPIRING status |

Changing trial days from 15 → 30 does **not** move an existing trial’s end date.

---

## What happens on approve

If trial is **on**: the new tenant gets a `TRIAL` subscription with `trial_starts_at` / `trial_ends_at` set to now + `trial_days`.

If trial is **off**: the owner can log in, but billing is locked (402) until Master assigns a plan or starts a trial from **Businesses**.

---

## Per-business trial

Master can **Start / extend trial** on an existing business (1–365 days). That is independent of the global default after the fact.

The **Trials** page lists trials that have not yet ended.

---

## After trial

When `trial_ends_at` passes, status becomes `EXPIRED` (via refresh or the expiry job). Login remains; billing locks. Master then assigns a paid/complimentary plan or records a manual renewal.

Related: [subscription-management.md](./subscription-management.md)
