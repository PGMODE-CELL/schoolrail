# SchoolRail Architecture

## System Overview

SchoolRail is a comprehensive school transport management system with the following components:

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Admin)                        │
│                    Next.js 14 + TypeScript                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Backend API                            │
│                     FastAPI + Python                         │
│                   (Port 3001)                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database                                │
│              SQLite (dev) / PostgreSQL (prod)               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Backend (FastAPI)
- **Location**: `backend/`
- **Port**: 3001
- **Database**: SQLAlchemy ORM
- **Authentication**: JWT tokens

#### Modules:
- `app/api/` - REST API endpoints
- `app/models/` - Database models
- `app/schemas/` - Pydantic schemas
- `app/services/` - Business logic
- `app/core/` - Configuration and security

### 2. Admin Panel (Next.js)
- **Location**: `admin/`
- **Port**: 3000
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS

#### Pages:
- Dashboard (`/dashboard`)
- Vehicles (`/dashboard/vehicles`)
- Drivers (`/dashboard/drivers`)
- Students (`/dashboard/students`)
- Routes (`/dashboard/routes`)
- Attendance (`/dashboard/attendance`)
- Fees (`/dashboard/fees`)
- Reports (`/dashboard/reports`)
- Map (`/dashboard/map`)
- Settings (`/dashboard/settings`)

### 3. Parent App (React Native/Expo)
- **Location**: `parent-app/`
- **Features**:
  - View child attendance
  - Track bus location
  - View fee payments
  - Receive notifications

### 4. Driver App (React Native/Expo)
- **Location**: `driver-app/`
- **Features**:
  - View assigned routes
  - Mark student attendance
  - Update vehicle status
  - Navigation

## Data Models

### Core Entities:
- **User** - Authentication users
- **School** - School information
- **Vehicle** - Bus/van fleet
- **Driver** - Driver profiles
- **Student** - Student records
- **Route** - Route definitions
- **Attendance** - Daily attendance
- **Fee** - Fee structures
- **Payment** - Payment records
- **Notification** - System notifications

## API Flow

1. User logs in → receives JWT token
2. Token sent in Authorization header
3. Backend validates token
4. Return appropriate data

## Security

- Password hashing (bcrypt)
- JWT tokens (15 min expiry)
- CORS configuration
- Input validation
- SQL injection prevention (SQLAlchemy)

## Deployment

### Development:
```bash
# Backend
cd backend
python main.py

# Frontend
cd admin
npm run dev
```

### Production (Docker):
See `docker/` folder for configurations.