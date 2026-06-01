# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-06-01

### Added — Global Scale Architecture

#### Multi-Tenant Infrastructure
- Database-per-tenant with PgBouncer connection pooling
- Tenant service: provision, migrate, decommission, credential rotation
- Redis-cached tenant registry (TTL 300s, auto-refresh)
- Shared PostgreSQL (Citus) for global registry (tenants, users)

#### Microservice Architecture
- **API Gateway** — Kong with rate limiting (Redis Lua), JWT auth, tenant resolution
- **Auth Service** — Register, login, refresh, logout, SSO/OAuth2, RS256 rotating keys
- **Fleet Service** — Vehicles, drivers, maintenance scheduling
- **Routing Service** — Routes, stops, async TSP route optimization
- **Student Service** — Students, attendance (batch), RFID ridership
- **Geo Service** — Real-time GPS, WebSocket streaming (100k concurrent), geofencing
- **Tenant Service** — Full tenant lifecycle management

#### Async Workers (Celery)
- 4 worker queues: optimization, reports, notifications, sync
- Route optimizer (nearest-neighbor TSP heuristic)
- Report generator (PDF, CSV, Excel)
- Notification sender (FCM push, SMTP email)
- Offline sync processor (conflict resolution: last-writer-wins)

#### Offline-First Mobile Apps
- SyncEngine: queue-based offline sync with retry (max 5), AsyncStorage persistence
- NetInfo listener for automatic sync on reconnect
- cachedFetch: AsyncStorage cache with TTL per endpoint
- Offline indicators (yellow banner with "X min ago" timestamps)
- All screens: cache-first → background refresh → error/empty states
- All 11 screens rewritten (parent + driver)

#### Observability Stack
- OpenTelemetry Collector with OTLP gRPC/HTTP receivers
- Prometheus with 10 alerting rules (error rate, latency, pod down, OOM)
- Grafana dashboards: service overview + tenant health (12 panels each)
- Jaeger distributed tracing
- Loki structured log aggregation

#### Infrastructure-as-Code
- **Terraform**: EKS, RDS (multi-AZ + read replicas), Redis cluster, RabbitMQ, Vault
- **Helm charts**: Kong gateway, auth-service, tenant-service (+ PgBouncer sidecar)
- **K8s configs**: Namespaces, network policies (default deny), PodSecurityPolicies, OTEL
- **CI/CD**: ArgoCD ApplicationSet + GitHub Actions (lint → test → build → migrate → deploy → smoke → rollback)
- **Docker Compose**: All 16 services for local development

#### Security
- JWT RS256 with rotating keys (Vault-managed)
- Rate limiting: per-tenant, per-endpoint, sliding window (Redis Lua)
- Immutable audit logging (all mutations logged with user/tenant/timestamp)
- Encryption: AES-256 at rest, TLS 1.3 in transit
- Dynamic DB credentials via Vault

### Changed
- Backend restructured from monolithic FastAPI to 8 microservices
- Admin panel API URL now points to Kong gateway (port 8000)
- Mobile apps rewritten for offline-first architecture
- Database schema migrated to per-tenant isolation model

### Removed
- Old monolithic backend (`backend/` → `backend_old/`)

## [1.0.0] - 2026-05-11

### Added
- Complete Backend API with FastAPI
  - Authentication (JWT), Schools, Vehicles, Drivers, Students, Routes
  - Attendance tracking, Fee management, GPS tracking, Analytics
- Admin Panel (Next.js 14) with dashboard, CRUD, live map
- Parent Mobile App (React Native/Expo)
- Driver Mobile App (React Native/Expo)
- Docker configuration, test suite, deployment guides
- Premium features: RFID ridership, geofencing, field trips, maintenance scheduling, trip stop logs, route optimization, emergency broadcast
- Admin CRUD modals: vehicles, drivers, students, routes
- Open source infrastructure: LICENSE, CODE_OF_CONDUCT, SECURITY.md, CONTRIBUTING.md, CI/CD

## [0.0.1] - 2024-01-01

### Added
- Initial project structure
- Basic scaffold
