# Business Rules

- One tenant per approved business registration.
- Bills, stock, and audit rows always scoped by `business_id` / tenant context.
- Medical Store / pharmacy workflows are permanently out of scope.
- Subscription/trial gates access; expired tenants are read-restricted per platform policy.
- Industry modules activate only for matching business type.

See also Common Modules and each business pack under `05-businesses/`.
