# API Architecture

Base: `/api/v1` · Envelope `{ success, data, meta, error }`

Common prefixes exist today: `/auth`, `/master`, `/bills`, `/items`, `/reports`, …

Industry namespaces (future): `/restaurant`, `/cafe`, `/grocery`, … `/travel`

Never authorize using client-supplied `tenant_id`.
