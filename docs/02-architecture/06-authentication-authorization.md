# Authentication

| Actor | Entry |
|-------|-------|
| Business users | `/login` |
| Master Admin | Footer dot → `/master/login` |

JWT; logout/password change bumps `token_version`. Registration does not issue JWT until approve.

---

# Authorization

RBAC: OWNER · BILLING_USER · MANAGER (target) + industry roles only when needed.

Guards: `auth_required`, `master_required`, subscription 402 gate, module entitlements.

