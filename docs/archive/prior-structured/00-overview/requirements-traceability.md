# Requirements Traceability

Every industry requirement should map:

```
Requirement ID
  → Feature
  → Module
  → Database Entity
  → API Endpoint
  → Frontend Page
  → Test Case
  → Sprint / Phase
```

## Example (Restaurant)

| Layer | Artifact |
|-------|----------|
| Requirement | `REST-REQ-004` Table management |
| Feature | Table Management |
| Module | Restaurant Tables |
| Entity | `RestaurantTable` |
| API | `GET/POST /api/v1/restaurant/tables` |
| UI | Tables page |
| Test | `TEST-REST-001` |
| Sprint | Restaurant pack sprint (see 12-sprints) |

Each business folder contains the linked artifacts (`requirements.md`, `features.md`, … `testing.md`, `roadmap.md`).
