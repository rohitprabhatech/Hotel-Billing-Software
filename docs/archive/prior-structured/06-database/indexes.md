# Indexes (Guidelines)

Always index `(tenant_id, …)` on hot tables. Unique per tenant: email, SKU, bill_number, IMEI/ISBN as applicable. Follow `parent_key` pattern for nullable hierarchy uniques.
