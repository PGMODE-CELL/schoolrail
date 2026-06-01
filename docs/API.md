# API Reference

Base URL: `http://localhost:8000/api/v1`

## Authentication

All endpoints (except `/auth/login`, `/auth/register`, `/auth/sso/*`) require a JWT token:

```
Authorization: Bearer <token>
```

### Auth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user + tenant |
| POST | `/auth/login` | Login, returns JWT pair |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Blacklist current token |
| GET | `/auth/me` | Current user profile |
| POST | `/auth/change-password` | Change password |
| GET | `/auth/sso/{provider}` | OAuth login (Google, Microsoft) |

**Login Request:**
```json
{ "email": "admin@your-school.edu", "password": "your-password" }

**Login Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "admin@your-school.edu",
    "full_name": "Your Name",
    "roles": ["admin"],
    "tenant_id": "uuid"
  }
}
}
```

## Fleet Service

Base: `/api/v1/fleet`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/vehicles` | List all vehicles |
| POST | `/vehicles` | Create vehicle |
| GET | `/vehicles/{id}` | Get vehicle details |
| PUT | `/vehicles/{id}` | Update vehicle |
| DELETE | `/vehicles/{id}` | Delete vehicle |
| GET | `/drivers` | List all drivers |
| POST | `/drivers` | Create driver |
| GET | `/drivers/{id}` | Get driver details |
| PUT | `/drivers/{id}` | Update driver |
| DELETE | `/drivers/{id}` | Delete driver |
| POST | `/vehicles/{id}/assign-driver` | Assign driver to vehicle |
| GET | `/vehicles/{id}/maintenance-history` | Get maintenance records |
| POST | `/maintenance/schedule` | Schedule maintenance |
| GET | `/maintenance/upcoming` | Upcoming maintenance tasks |

## Routing Service

Base: `/api/v1/routing`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/routes` | List all routes |
| POST | `/routes` | Create route |
| GET | `/routes/{id}` | Get route details |
| PUT | `/routes/{id}` | Update route |
| DELETE | `/routes/{id}` | Delete route |
| POST | `/routes/{id}/optimize` | Start async route optimization |
| GET | `/routes/{id}/optimize/{task_id}/status` | Check optimization status |
| GET | `/stops` | List all stops |
| POST | `/stops` | Create stop |
| PUT | `/stops/{id}` | Update stop |
| DELETE | `/stops/{id}` | Delete stop |
| POST | `/trip-stops/arrive` | Mark arrival at stop |
| POST | `/trip-stops/depart` | Mark departure from stop |

## Student Service

Base: `/api/v1/students`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/students` | List all students |
| POST | `/students` | Create student |
| GET | `/students/{id}` | Get student details |
| PUT | `/students/{id}` | Update student |
| DELETE | `/students/{id}` | Delete student |
| POST | `/attendance/batch` | Bulk mark attendance |
| GET | `/attendance/daily` | Daily attendance report |
| POST | `/ridership/check-in` | RFID check-in |
| POST | `/ridership/check-out` | RFID check-out |
| GET | `/ridership/trip/{id}` | Trip ridership log |

## Geo Service

Base: `/api/v1/geo`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/position` | Push GPS position (driver) |
| GET | `/vehicle/{id}/live` | Get vehicle live position |
| WS | `/vehicle/{id}/stream` | WebSocket live position stream |
| POST | `/geofence/zones` | Create geofence zone |
| GET | `/geofence/zones` | List geofence zones |
| POST | `/geofence/check` | Check position against zones |
| GET | `/proximity-alerts` | Get proximity alerts |

## Tenant Service

Base: `/api/v1/tenants`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tenants` | Provision new tenant (DB + migrations) |
| GET | `/tenants/{id}` | Get tenant details |
| GET | `/tenants/{id}/status` | Tenant database health |
| POST | `/tenants/{id}/migrate` | Run migrations |
| DELETE | `/tenants/{id}` | Decommission tenant |
| POST | `/tenants/{id}/rotate-secret` | Rotate DB credentials |

## Error Responses

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Email is required",
  "details": { "field": "email" }
}
```

Common codes: `VALIDATION_ERROR`, `AUTH_ERROR`, `NOT_FOUND`, `RATE_LIMITED`, `TENANT_ERROR`, `INTERNAL_ERROR`

## Rate Limiting

Headers returned on every response:
- `X-RateLimit-Limit`: max requests per window
- `X-RateLimit-Remaining`: remaining requests
- `X-RateLimit-Reset`: window reset time (Unix)

On rate limit (429):
```json
{
  "code": "RATE_LIMITED",
  "message": "Too many requests. Retry after 30 seconds.",
  "details": { "retry_after": 30 }
}
```

## WebSocket Events

### Position Stream (`ws://localhost:8000/ws/vehicle/{id}/stream`)

**Client → Server:**
```json
{ "type": "position", "lat": 28.6139, "lng": 77.2090, "speed": 45, "heading": 180 }
```

**Server → Client:**
```json
{ "type": "position_update", "vehicle_id": "uuid", "lat": 28.6139, "lng": 77.2090, "speed": 45, "heading": 180, "timestamp": "2026-06-01T10:30:00Z" }
```
