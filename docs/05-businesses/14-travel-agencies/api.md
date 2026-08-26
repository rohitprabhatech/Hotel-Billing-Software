# Travel Agencies — API

Namespace: `/api/v1/travel/...` (also `/api/v1/tour-packages`)

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/tour-packages` | Package list / create | JWT | items.read/write + `tour_packages` | Yes |
| GET/PATCH | `/api/v1/tour-packages/{id}` | Detail / update | JWT | as above | Yes |
| POST | `/api/v1/tour-packages/{id}/bill` | Service bill (qty × package) | JWT | billing | Yes |
| GET/POST | `/api/v1/travel/packages` | Aliases | JWT | as above | Yes |
| POST | `/api/v1/travel/packages/{id}/bill` | Bill alias | JWT | billing | Yes |
| GET/POST | `/api/v1/travel-bookings` | Bookings (`TB-#####`) | JWT | billing + `travel_bookings` | Yes |
| PATCH | `/api/v1/travel-bookings/{id}/status` | Status pipeline | JWT | Owner/Manager | Yes |
| POST | `/api/v1/travel-bookings/{id}/payments` | Advance / remaining | JWT | billing | Yes |
| GET/POST | `/api/v1/travel/bookings` | Booking aliases | JWT | as above | Yes |
| GET/POST | `/api/v1/travel/bookings/{id}/itinerary` | Itinerary (hotel/vehicle/ticket/…) | JWT | Owner/Manager write | Yes |
| PATCH/DELETE | `/api/v1/travel/bookings/{id}/itinerary/{item_id}` | Update / remove line | JWT | Owner/Manager | Yes |
| GET/POST | `/api/v1/travel/bookings/{id}/documents` | Document metadata | JWT | Owner/Manager write | Yes |
| DELETE | `/api/v1/travel/bookings/{id}/documents/{doc_id}` | Remove metadata (audited) | JWT | Owner/Manager | Yes |
| GET/POST | `/api/v1/travel-agents` | Agent CRUD | JWT | billing + `travel_commission` | Yes |
| PATCH | `/api/v1/travel-agents/{id}` | Update agent | JWT | Owner/Manager | Yes |
| GET/POST | `/api/v1/commissions` | List / accrue commission | JWT | as above | Yes |
| GET | `/api/v1/commissions/report` | Totals by agent | JWT | billing | Yes |
| PATCH | `/api/v1/commissions/{id}/status` | PENDING / PAID / CANCELLED | JWT | Owner/Manager | Yes |
| * | `/api/v1/travel/agents`, `/travel/commissions` | Aliases | JWT | as above | Yes |

## Contract notes

- Packages link to an untracked catalog `item_id` (`stock_quantity` always `null`) so `/bills` works without stock moves.
- Billing users can list packages and create bills; Owner/Manager manage catalog.
- Itinerary `item_type`: `HOTEL` / `VEHICLE` / `TICKET` / `ACTIVITY` / `OTHER`. Documents: metadata only (no binary); PII encrypt-at-rest later.
- Commission = `money(booking_total × commission_percent / 100)`. Booking create may pass `agent_id` (uses agent default %) or override `commission_percent`. One entry per booking.
- **Authentication:** Bearer JWT. **Tenant scope:** from JWT only.

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
