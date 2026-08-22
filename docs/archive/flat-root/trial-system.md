# Trial System — Prabha Billing SaaS V2

## Defaults

- Free trial **enabled**  
- Duration **15 days** (Master-configurable)  
- Applies to **newly approved** businesses when enabled  

Changing global days does **not** rewrite existing trials.

## Master settings

`trial_enabled`, `trial_days`, `expiry_warning_days` (platform_settings).

## Lifecycle

Approve → if trial on → `TRIAL` subscription → Owner login → billing allowed until end → EXPIRING notices → EXPIRED lockout unless renewed.

## If trial off

Approval creates owner login; billing stays locked until Master assigns plan or starts trial.
