# Migration Strategy

1. Backup + inspect  
2. Additive Alembic/helpers only  
3. Map legacy `business_type` strings → 14-type catalog  
4. Never `02_schema.sql` on live  
5. Stamp after helpers on Hostinger MariaDB  
6. No DROP/DELETE production data without explicit approval  

Documentation phase creates **zero** migrations.
