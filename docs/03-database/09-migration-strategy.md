# Migration Strategy

1. Backup + inspect  
2. Additive Alembic/helpers only  
3. Map legacy `business_type` strings → 14-type catalog  
4. Never `02_schema.sql` on live  
5. Stamp after helpers on Hostinger MariaDB (Phase 8 stamp script, then `flask db upgrade` for industry)  
6. No DROP/DELETE production data without explicit approval  

**Industry ops runbook (BIZ-67):** [`10-industry-modules-ops-runbook.md`](./10-industry-modules-ops-runbook.md)  
**Ordered revision list:** [`11-alembic-revision-order.md`](./11-alembic-revision-order.md)

Documentation phase creates **zero** migrations unless the sprint explicitly ships Alembic.
