# SchoolRail — Complete School Transportation Management System

[![CI/CD Pipeline](https://github.com/schoolrail/schoolrail/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/schoolrail/schoolrail/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![React Native](https://img.shields.io/badge/React%20Native-0.73-blueviolet.svg)](https://reactnative.dev/)

A production-ready school bus tracking and transportation management system built with modern technologies.

## Features

### Admin Panel (Next.js + TypeScript)
- **Dashboard** — Real-time analytics with charts and statistics
- **Vehicles** — Complete fleet management with status tracking
- **Drivers** — Driver profiles, assignments, and performance
- **Routes** — Route creation, stop management, and optimization
- **Students** — Student enrollment and route assignments
- **Attendance** — Daily attendance tracking with reports
- **Fees** — Fee management and payment tracking
- **Reports** — Comprehensive reports with export (PDF, Excel, CSV)
- **Live Map** — Real-time vehicle tracking with OpenStreetMap
- **Settings** — School profile, account management

### Parent App (React Native + Expo)
- **Home** — Dashboard with child info and quick actions
- **Live Tracking** — Real-time bus location
- **Attendance** — Child's attendance history
- **Fees** — View and pay fees
- **Profile** — Account management

### Driver App (React Native + Expo)
- **Home** — Today's schedule and routes
- **Routes** — All assigned routes
- **Attendance** — Mark student attendance
- **Vehicle** — Vehicle status and maintenance
- **Profile** — Driver profile

### Backend (Python FastAPI)
- **JWT Authentication** — Secure role-based access (admin, driver, parent)
- **RESTful API** — Full CRUD for vehicles, drivers, students, routes
- **GPS Tracking** — Real-time vehicle location with geofencing
- **Attendance** — Daily student attendance with history
- **Fee Management** — Fee tracking and payment recording
- **Report Generation** — PDF, Excel, CSV exports
- **Broadcasting** — WebSocket-based notifications and alerts

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Admin** | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| **Mobile** | React Native, Expo SDK 50, React Navigation |
| **API** | Python FastAPI 0.109+ |
| **Database** | SQLite (dev) / PostgreSQL 14+ (prod) |
| **Cache** | Redis 6+ (optional) |
| **Auth** | JWT + OAuth2 |
| **Maps** | Leaflet, OpenStreetMap |
| **Real-time** | WebSocket |

## Project Structure

```
schoolrail/
├── admin/                    # Next.js Admin Panel
│   ├── src/
│   │   ├── app/              # App router pages
│   │   ├── components/       # UI components
│   │   │   ├── charts/       # Chart components
│   │   │   └── ui/           # Shared UI (EmptyState)
│   │   ├── context/          # Auth context
│   │   ├── hooks/            # Custom hooks (useSchoolRail, useWebSocket)
│   │   └── lib/              # API client (api.ts)
│   └── package.json
│
├── parent-app/               # React Native Parent App
│   ├── App.tsx
│   ├── src/
│   │   ├── screens/          # App screens
│   │   ├── navigation/       # Tab navigator
│   │   ├── context/          # Auth context
│   │   ├── theme/            # Colors, typography
│   │   └── config/           # API base URL, helpers
│   └── package.json
│
├── driver-app/               # React Native Driver App
│   ├── App.tsx
│   ├── src/
│   │   ├── screens/          # App screens
│   │   ├── navigation/       # Tab navigator
│   │   ├── context/          # Auth context
│   │   ├── theme/            # Colors, typography
│   │   └── config/           # API base URL, helpers
│   └── package.json
│
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/ # API endpoint routers
│   │   │   ├── auth/         # Authentication
│   │   │   ├── routes/       # Routes & stops
│   │   │   ├── students/     # Student management
│   │   │   ├── attendance/   # Attendance tracking
│   │   │   ├── gps/          # GPS tracking
│   │   │   └── remaining.py  # Fees, schools, vehicles, drivers, etc.
│   │   ├── core/             # Config
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   ├── main.py
│   └── requirements.txt
│
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── INSTALL.md
└── package.json              # Root workspace config
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py
# → http://localhost:3001

# Admin Panel (separate terminal)
cd admin
npm install
npm run dev
# → http://localhost:3000

# Default login: admin@schoolrail.com / admin123
```

## API Endpoints

| Category | Endpoints |
|----------|-----------|
| **Auth** | `POST /auth/login`, `POST /auth/register`, `POST /auth/change-password`, `POST /auth/logout`, `POST /auth/verify`, `GET /auth/me`, `PUT /auth/me` |
| **Schools** | `GET /schools`, `POST /schools`, `PUT /schools/{id}` |
| **Vehicles** | `GET /vehicles`, `POST /vehicles`, `GET /vehicles/{id}`, `PUT /vehicles/{id}`, `DELETE /vehicles/{id}`, `GET /vehicles/active` |
| **Drivers** | `GET /drivers`, `POST /drivers`, `GET /drivers/{id}`, `PUT /drivers/{id}`, `DELETE /drivers/{id}` |
| **Routes** | `GET /routes`, `POST /routes`, `GET /routes/{id}`, `PUT /routes/{id}`, `DELETE /routes/{id}`, `POST /routes/{id}/optimize` |
| **Students** | `GET /students`, `POST /students`, `GET /students/{id}`, `PUT /students/{id}`, `DELETE /students/{id}` |
| **Attendance** | `GET /attendance`, `POST /attendance`, `GET /attendance/daily`, `GET /attendance/student/{id}` |
| **Fees** | `GET /fees`, `POST /fees`, `GET /fees/{id}`, `PUT /fees/{id}`, `DELETE /fees/{id}`, `POST /fees/{id}/pay` |
| **GPS** | `GET /gps/active`, `GET /gps/vehicle/{id}`, `GET /gps/history/{id}`, `POST /gps/update`, `POST /gps/location/batch`, `POST /gps/geofence/check` |
| **Notifications** | `GET /notifications`, `POST /notifications`, `PUT /notifications/{id}/read`, `POST /notifications/broadcast` |
| **Alerts** | `GET /alerts`, `POST /alerts`, `PUT /alerts/{id}` |
| **Analytics** | `GET /analytics/dashboard`, `GET /analytics/vehicles`, `GET /analytics/routes`, `GET /analytics/drivers`, `GET /analytics/attendance`, `GET /analytics/fees`, `GET /analytics/alerts` |
| **Trips** | `GET /trips`, `POST /trips`, `GET /trips/{id}`, `GET /trips/active` |
| **Reports** | `GET /reports/attendance`, `GET /reports/fees`, `GET /reports/students`, `GET /reports/vehicles` |

Full interactive docs at `/docs` when the backend is running.

## Default Credentials

| Role   | Email                     | Password   |
|--------|---------------------------|------------|
| Admin  | admin@schoolrail.com      | admin123   |
| Driver | driver1@schoolrail.com    | admin123   |
| Parent | parent1@schoolrail.com    | admin123   |

## Documentation

- [Installation Guide](INSTALL.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Running with Docker

```bash
docker-compose up --build
# Admin: http://localhost:3000
# API:   http://localhost:3001
```

## Roadmap

- [x] Core admin panel (vehicles, drivers, students, routes, attendance, fees)
- [x] Real-time GPS tracking
- [x] Mobile apps (parent + driver)
- [x] Report generation (PDF, Excel, CSV)
- [ ] Push notifications (FCM)
- [ ] Payment gateway integration
- [ ] Route optimization (advanced)
- [ ] SMS / Email alerts
- [ ] Multi-school / tenant support

## License

MIT — see [LICENSE](LICENSE)

---

<p align="center">Made for safer, smarter school transportation</p>
