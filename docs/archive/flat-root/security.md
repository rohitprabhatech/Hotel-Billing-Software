# Security — Prabha Billing SaaS V2

## Controls

| Area | Approach |
|------|----------|
| Authentication | JWT + token_version; hashed passwords |
| Authorization | RBAC + master_required + module gates |
| Tenant isolation | Server-side tenant context only |
| Input validation | Schemas / service checks |
| SQL injection | ORM parameterized queries |
| XSS | React escaping; CSP headers via proxy where possible |
| CORS | Explicit origins |
| Rate limiting | Flask-Limiter (configure storage for prod) |
| Secrets | Env only; never commit `.env` |
| Audit | Tenant + platform ledgers |
| Backup | See backup-and-recovery.md |
| Privacy | See privacy-policy.md (**legal review**) |

## Never expose

DB password · JWT secret · SMTP password · WhatsApp tokens · Payment gateway keys · API keys

## Claims

Do **not** claim ISO/PCI/legal compliance without verification. Mark counsel review on privacy/terms.
