# SchoolRail API Documentation

## Base URL
```
http://localhost:3001
```

## Authentication
All endpoints (except login/register) require JWT authentication.
Include in header:
```
Authorization: Bearer <token>
```

## Endpoints Overview

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | User login |
| POST | /api/v1/auth/register | User registration |
| GET | /api/v1/auth/me | Get current user |

### Schools
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/schools | List all schools |
| POST | /api/v1/schools | Create school |
| GET | /api/v1/schools/{id} | Get school |
| PUT | /api/v1/schools/{id} | Update school |
| DELETE | /api/v1/schools/{id} | Delete school |

### Vehicles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/vehicles | List all vehicles |
| POST | /api/v1/vehicles | Create vehicle |
| GET | /api/v1/vehicles/{id} | Get vehicle |
| PUT | /api/v1/vehicles/{id} | Update vehicle |
| DELETE | /api/v1/vehicles/{id} | Delete vehicle |

### Drivers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/drivers | List all drivers |
| POST | /api/v1/drivers | Create driver |
| GET | /api/v1/drivers/{id} | Get driver |
| PUT | /api/v1/drivers/{id} | Update driver |
| DELETE | /api/v1/drivers/{id} | Delete driver |

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/students | List all students |
| POST | /api/v1/students | Create student |
| GET | /api/v1/students/{id} | Get student |
| PUT | /api/v1/students/{id} | Update student |
| DELETE | /api/v1/students/{id} | Delete student |

### Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/routes | List all routes |
| POST | /api/v1/routes | Create route |
| GET | /api/v1/routes/{id} | Get route |
| PUT | /api/v1/routes/{id} | Update route |
| DELETE | /api/v1/routes/{id} | Delete route |

### Attendance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/attendance | List attendance |
| POST | /api/v1/attendance | Mark attendance |
| GET | /api/v1/attendance/{id} | Get attendance |

### Fees
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/fees | List fees |
| POST | /api/v1/fees | Create fee |
| PUT | /api/v1/fees/{id} | Update fee |
| POST | /api/v1/fees/{id}/pay | Process payment |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/analytics/overview | Dashboard overview |
| GET | /api/v1/analytics/attendance | Attendance stats |
| GET | /api/v1/analytics/revenue | Revenue stats |

## Example Requests

### Login
```bash
curl -X POST http://localhost:3001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Get Vehicles
```bash
curl -X GET http://localhost:3001/api/v1/vehicles \
  -H "Authorization: Bearer <token>"
```

## Error Codes
- 200: Success
- 401: Unauthorized
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error