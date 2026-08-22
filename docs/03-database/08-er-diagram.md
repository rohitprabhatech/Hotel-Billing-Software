# ER Diagrams

```mermaid
erDiagram
  TENANT ||--o{ BILL : has
  BILL ||--|{ BILL_ITEM : contains
  TENANT ||--o{ PRODUCT : has
  BUSINESS_TYPE ||--o{ TENANT : classifies
```

Per-industry diagrams: see each business `database.md` + workflow mermaid.
