# Master Admin — Prabha Billing SaaS V2

## Identity

Prabha Technology operators in `master_admins` — **not** tenant users.

## Login UX (security)

1. Public site footer → subtle **dot**  
2. `/master/login` — Email, Password, Sign In only  
3. No Register / Forgot Password on this page  
4. Owner credentials fail with generic invalid message  

## Capabilities

| Area | Actions |
|------|---------|
| Registration | Approve / reject |
| Businesses | Activate / deactivate / assign plan / trial / renew / cancel / suspend billing |
| Business types | Manage catalog + module matrix (**V2**) |
| Modules / features | Platform catalog (**V2**) |
| Plans | CRUD, visibility, active flag, limits |
| Trial | Enable/disable, days, warning window |
| Notifications | Platform bell |
| Audit | Platform audit log |
| Settings | System settings |
| Jobs | Expiry check |

## Seed (ops)

```powershell
cd backend
# MASTER_ADMIN_EMAIL / MASTER_ADMIN_PASSWORD in .env (do not commit)
.\.venv\Scripts\python.exe scripts\seed_master_admin.py
```

Live DB may still have `master_admins = 0` until this succeeds.

## Dashboard KPIs (current)

Deep-link to filtered businesses (`tenant_status`, subscription `status`) — keep and extend for V2 metrics.
