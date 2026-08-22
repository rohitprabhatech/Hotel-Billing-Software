# Registration Approval Flow — Business Billing

**Product:** Business Billing · Prabha Technology Pvt. Ltd.

Public signup is a **request queue**. A business is created only when Master Admin approves.

---

## Flow

```text
Landing → Register Business → PENDING registration_requests
        → (no tenant, no JWT, login blocked)

Master → Registration requests → Approve
        → tenants (ACTIVE) + users (OWNER, email_verified)
        → optional TRIAL subscription
        → approval email with /login

Master → Reject (reason ≥ 8 chars)
        → no tenant
        → rejection email
        → same email may register again
```

Terms of Service and Privacy Policy must be accepted (`terms_accepted: true`) or the API returns 400.

---

## What is stored on the request

Business name/type, owner name/email, hashed password, optional address/mobile/GST/FSSAI. Detail APIs **never** return `password` or `password_hash`.

Duplicate pending email → 409. Email already used by a user or Master Admin → 409.

---

## After approve

- Owner signs in at `/login` (not `/master/login`).
- If trial is enabled, remaining trial days show in Owner Settings / `/auth/me`.
- If trial is disabled, billing is locked until Master assigns a plan.

Legacy `POST /api/v1/auth/register-hotel` remains an alias of register-business.

Related: [master-admin-manual.md](./master-admin-manual.md) · [trial-management.md](./trial-management.md)
