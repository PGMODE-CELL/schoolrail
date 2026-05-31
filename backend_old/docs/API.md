# SchoolRail API Documentation

## Base URL
```
http://localhost:3001/api/v1
```

## Authentication

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "admin@schoolrail.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "usr_001",
    "email": "admin@schoolrail.com",
    "name": "Admin",
    "role": "admin"
  }
}
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "parent"
}
```

## Vehicles

### List Vehicles
```http
GET /vehicles
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "veh_001",
      "vehicle_number": "SR-001",
      "vehicle_type": "Bus",
      "capacity": 50,
      "status": "active",
      "driver_id": "drv_001",
      "last_maintenance": "2024-01-15",
      "next_maintenance": "2024-02-15"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25
  }
}
```

### Create Vehicle
```http
POST /vehicles
Authorization: Bearer <token>
Content-Type: application/json

{
  "vehicle_number": "SR-025",
  "vehicle_type": "Van",
  "capacity": 15,
  "model": "Toyota Hiace",
  "year": 2023
}
```

### Update Vehicle
```http
PUT /vehicles/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "maintenance"
}
```

### Delete Vehicle
```http
DELETE /vehicles/:id
Authorization: Bearer <token>
```

## Routes

### List Routes
```http
GET /routes
Authorization: Bearer <token>
```

### Create Route
```http
POST /routes
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Route 1 - North",
  "start_point": "School",
  "end_point": "Sector 15",
  "stops": [
    {"name": "Stop 1", "lat": 28.6139, "lng": 77.2090},
    {"name": "Stop 2", "lat": 28.6150, "lng": 77.2100}
  ],
  "distance": 12.5,
  "estimated_time": 45
}
```

## Students

### List Students
```http
GET /students
Authorization: Bearer <token>
Query Parameters:
  - route_id: Filter by route
  - class: Filter by class
  - section: Filter by section
  - search: Search by name
```

### Create Student
```http
POST /students
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Smith",
  "class": "Class 5",
  "section": "A",
  "father_name": "Robert Smith",
  "phone": "+91 9876543210",
  "address": "123 Main St",
  "route_id": "rte_001",
  "pickup_point": "Stop 1"
}
```

### Update Student
```http
PUT /students/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "route_id": "rte_002",
  "pickup_point": "Stop 3"
}
```

### Delete Student
```http
DELETE /students/:id
Authorization: Bearer <token>
```

## Attendance

### Mark Attendance
```http
POST /attendance
Authorization: Bearer <token>
Content-Type: application/json

{
  "date": "2024-01-20",
  "route_id": "rte_001",
  "records": [
    {"student_id": "std_001", "status": "present"},
    {"student_id": "std_002", "status": "absent"},
    {"student_id": "std_003", "status": "leave"}
  ]
}
```

### Get Attendance
```http
GET /attendance
Authorization: Bearer <token>
Query Parameters:
  - date: Specific date
  - start_date: Start of range
  - end_date: End of range
  - route_id: Filter by route
```

## Fees

### List Fees
```http
GET /fees
Authorization: Bearer <token>
```

### Create Fee
```http
POST /fees
Authorization: Bearer <token>
Content-Type: application/json

{
  "student_id": "std_001",
  "amount": 5000,
  "due_date": "2024-02-28",
  "description": "Term 1 Fee"
}
```

### Pay Fee
```http
POST /fees/:id/pay
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_method": "online",
  "transaction_id": "TXN123456"
}
```

## Drivers

### List Drivers
```http
GET /drivers
Authorization: Bearer <token>
```

### Create Driver
```http
POST /drivers
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Mike Johnson",
  "phone": "+91 9876543211",
  "email": "mike@example.com",
  "license_number": "DL12345678",
  "assigned_vehicle": "veh_001"
}
```

## Reports

### Generate Report
```http
POST /reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "attendance",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "format": "pdf",
  "route_id": "rte_001"
}
```

### Available Report Types
```http
GET /reports/types
Authorization: Bearer <token>
```

## Analytics

### Dashboard Summary
```http
GET /analytics/dashboard
Authorization: Bearer <token>
```

### Route Analytics
```http
GET /analytics/routes
Authorization: Bearer <token>
Query Parameters:
  - route_id: Specific route
  - start_date: Start date
  - end_date: End date
```

### Student Analytics
```http
GET /analytics/students
Authorization: Bearer <token>
```

## Notifications

### Get Notifications
```http
GET /notifications
Authorization: Bearer <token>
```

### Mark as Read
```http
PUT /notifications/:id/read
Authorization: Bearer <token>
```

## WebSocket

### Connect
```ws
ws://localhost:3001/ws
Authorization: Bearer <token>
```

### Subscribe to Events
```json
{
  "type": "subscribe",
  "channel": "vehicle:location"
}
```

### Event Types
- `vehicle:location_update` - Real-time vehicle locations
- `attendance:marked` - Attendance updates
- `alert:new` - New alerts
- `trip:started` - Trip started
- `trip:completed` - Trip completed

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Validation error",
  "details": {
    "email": "Invalid email format"
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error"
}
```

## Rate Limiting

- **Authentication endpoints**: 10 requests/minute
- **API endpoints**: 100 requests/minute
- **WebSocket connections**: 5 per user

## Pagination

All list endpoints support pagination:
```
?page=1&limit=20
```

Response includes:
```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

## Sorting

Sort by any field:
```
?sort=created_at&order=desc
```

## Filtering

Filter by multiple fields:
```
?status=active&route_id=rte_001
```