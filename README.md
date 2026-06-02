# SchoolRail — Open Source School Transportation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![React Native](https://img.shields.io/badge/React%20Native-0.73-blueviolet.svg)](https://reactnative.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/K8s-Helm-326CE5.svg)](https://helm.sh)
[![Terraform](https://img.shields.io/badge/Terraform-1.7+-844FBA.svg)](https://terraform.io)

**The most complete, production-ready, open-source school transportation management system.**  
Built to scale from a single school to millions of institutions — for free.

> 🏆 **Why SchoolRail?** Unlike proprietary systems (Edulog, BusPlanner, Transfinder, Busology) that charge $5–$15/student/year, SchoolRail is MIT-licensed, self-hosted, and already more feature-complete than most paid alternatives.

---

## Features — Compared to Paid Competitors

| Feature | SchoolRail | Edulog | BusPlanner | Transfinder | Busology |
|---------|:----------:|:------:|:----------:|:-----------:|:--------:|
| **Route optimization** (TSP) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Real-time GPS tracking** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Parent mobile app** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Driver mobile app** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RFID attendance** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Geofencing** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Field trip management** | ✅ | ❌ | ✅ | ✅ | ❌ |
| **Maintenance scheduling** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Emergency broadcast** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Multi-tenant (1M+ schools)** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Offline-first mobile** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Async route optimization** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **OpenTelemetry observability** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **K8s native** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **SSO / OAuth** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **24/7 self-hosted** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Price** | **Free** | $5-12/student | $4-8/student | $6-15/student | $3-7/student |

---

## Architecture Overview

```
                                  ┌──────────────────┐
                                  │   API Gateway    │
                                  │  (FastAPI Proxy) │
                                  │ Rate Limit | Auth│
                                  └────────┬─────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
       ┌──────▼──────┐            ┌───────▼───────┐           ┌────────▼────────┐
       │  Auth Svc   │            │  Fleet Svc    │           │  Routing Svc    │
       │  :8001      │            │  :8002        │           │  :8003          │
       └──────┬──────┘            └───────┬───────┘           └────────┬────────┘
              │                            │                            │
       ┌──────▼──────┐            ┌───────▼───────┐           ┌────────▼────────┐
       │  Student    │            │  Payment      │           │  Geo            │
       │  Svc :8004  │            │  Svc :8007    │           │  Svc :8005      │
       └──────┬──────┘            └───────┬───────┘           └────────┬────────┘
              │                            │                            │
              └────────────────────────────┼────────────────────────────┘
                                           │
                                  ┌────────▼────────┐
                                  │   RabbitMQ      │
                                  │   Event Bus     │
                                  └────────┬────────┘
                                           │
                                  ┌────────▼────────┐
                                  │   Workers       │
                                  │ Route Opt/Notify│
                                  │ Reports/Sync    │
                                  └─────────────────┘
```

### Multi-Tenant Data Isolation

```
                    ┌─────────────────────┐
                    │  Global Registry    │
                    │  (Citus distributed)│
                    │  tenants, users     │
                    └──────┬──────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼─────┐ ┌───▼────┐ ┌────▼──────┐
       │ Tenant A   │ │Tenant B│ │ Tenant C  │
       │ PostgreSQL │ │  PG    │ │    PG     │
       │ (isolated) │ │(isol.) │ │ (isol.)   │
       └────────────┘ └────────┘ └───────────┘
```

**Every tenant gets an isolated PostgreSQL database.**  
Connection pooling via PgBouncer, cached lookups via Redis, zero cross-tenant data leakage.

---

## Tech Stack

| Layer | Technology | Scale |
|-------|-----------|-------|
| **Frontend (Admin)** | Next.js 14, TypeScript, Tailwind CSS, Recharts | SSR + CDN |
| **Mobile** | React Native 0.73, Expo SDK 50, WatermelonDB | Offline-first |
| **API Gateway** | FastAPI proxy + rate limit middleware | 100k req/s |
| **Microservices** | Python FastAPI 0.115+, asyncpg, SQLAlchemy async | Horizontal pod autoscaling |
| **Async Workers** | Celery + RabbitMQ + Redis | Separate worker pools |
| **Database** | PostgreSQL 16 + Citus (distributed) + PgBouncer | Read replicas, sharding |
| **Cache** | Redis Cluster | Sub-millisecond |
| **File Storage** | MinIO / S3 | Any S3-compatible |
| **Real-time** | WebSocket (Socket.IO) | 100k concurrent |
| **Auth** | JWT RS256 (rotating) + SSO/OAuth2 | Vault-managed keys |
| **Observability** | OpenTelemetry → Prometheus + Grafana + Jaeger + Loki | Distributed tracing |
| **Container** | Docker + K8s + Helm | Multi-region (any cloud) |
| **Infrastructure** | Terraform + Crossplane | GitOps via ArgoCD |
| **CI/CD** | GitHub Actions | Build → Test → Migrate → Deploy → Smoke → Rollback |

---

## Quick Start (5 minutes)

```bash
# Prerequisites: Docker Desktop + Git

git clone https://github.com/PGMODE-CELL/schoolrail.git
cd schoolrail

# Start all services
docker compose up -d

# Open the admin panel
open http://localhost:3000

# Register an admin account at http://localhost:3000
```

That's it. Admin panel, API gateway, all microservices, database, and monitoring are running.

### Platform-Specific Setup

Read the full [Installation Guide](INSTALL.md) for:
- **Production**: K8s + Helm + Terraform (`infrastructure/`)
- **Manual**: Without Docker (`backend/`, `admin/`, `parent-app/`, `driver-app/`)
- **Mobile**: Expo Go on physical devices

---

## Mobile Apps

| App | Users | Key Features |
|-----|-------|-------------|
| **Parent App** | Parents/Guardians | Live bus tracking, attendance history, fee payments, notifications, offline-first |
| **Driver App** | Bus Drivers | Route navigation, RFID attendance, GPS reporting, maintenance alerts, offline-first |

Both apps are **offline-first** — they work without internet and sync when connectivity returns.

```bash
cd parent-app      # or driver-app
npm install
npx expo start
```

---

## Project Structure

```
schoolrail/
├── backend/
│   ├── libs/shared/          # Multi-tenant DB, event bus, security, middleware
│   ├── services/
│   │   ├── gateway/          # API Gateway (rate limit, auth, tenant resolution)
│   │   ├── auth/             # Authentication + SSO service
│   │   ├── tenant/           # Tenant lifecycle management
│   │   ├── fleet/            # Vehicles, drivers, maintenance
│   │   ├── routing/          # Routes, stops, async optimization
│   │   ├── students/         # Students, attendance, ridership
│   │   ├── geo/              # Real-time GPS, WebSocket, geofencing
│   │   └── ...               # Payments, notifications, analytics
│   └── workers/              # Celery async workers (route opt, reports, notifications, sync)
├── admin/                    # Next.js 14 Admin Panel
├── parent-app/               # React Native Parent App (offline-first)
├── driver-app/               # React Native Driver App (offline-first)
├── infrastructure/
│   ├── terraform/            # Multi-region provisioning (AWS/GCP/Azure)
│   ├── helm/                 # K8s Helm charts (all services)
│   ├── k8s/                  # K8s configs (OTEL, Prometheus, Grafana)
│   └── cicd/                 # ArgoCD + GitHub Actions pipelines
└── docker-compose.yml        # Local development (all 16 services)
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Architecture](ARCHITECTURE.md) | Full platform design, service map, data flow |
| [Installation](INSTALL.md) | Docker, K8s, manual, cloud deployment |
| [API Reference](docs/API.md) | All endpoints, schemas, auth |
| [Contributing](CONTRIBUTING.md) | How to contribute code, docs, translations |
| [Security](SECURITY.md) | Vulnerability reporting, encryption, auth |
| [Changelog](CHANGELOG.md) | Release history and migration notes |

---

## Security

- **TLS 1.3** — All traffic encrypted in transit
- **AES-256** — Data encrypted at rest (database + S3)
- **JWT RS256** — Rotating signing keys via Vault
- **Tenant isolation** — Database-per-tenant + row-level security
- **Rate limiting** — Per-tenant, per-endpoint (Redis sliding window)
- **Audit logging** — Immutable, all mutations logged
- **Secrets management** — HashiCorp Vault with dynamic credentials
- **DDoS protection** — Cloudflare + WAF + rate limiting

---

## Scaling Model

| Tier | Schools | Architecture | Infrastructure |
|------|---------|-------------|----------------|
| **S** | 1–10 | Shared DB, single region | Docker Compose or single K8s cluster |
| **M** | 10–1k | Database-per-tenant, read replicas | K8s cluster, managed PostgreSQL |
| **L** | 1k–100k | Sharded tenant registry, Citus, Redis cache | Multi-AZ K8s, RDS + ElastiCache |
| **XL** | 100k–1M | Multi-region, tenant sharding, CDN | Global K8s, cross-region DB replication |
| **XXL** | 1M+ | Custom partitioning, geo-replication | Multi-cloud, custom data plane |

All tiers use the same codebase. Upgrade by adding infrastructure.

---

## Community

- 🌟 [Star on GitHub](https://github.com/PGMODE-CELL/schoolrail)
- 📧 [Security issues](SECURITY.md)
- 💖 [Sponsor on GitHub](.github/FUNDING.yml)

---

## License

MIT — see [LICENSE](LICENSE)  

**Free for any use** — personal, educational, commercial, government.  
No restrictions, no hidden fees, no telemetry.

---

<p align="center">
  <strong>SchoolRail</strong> — The free, open-source alternative to expensive school transportation software.<br>
  Built with ❤️ for safer, smarter student transportation worldwide.
</p>

<p align="center">
  <a href="https://github.com/PGMODE-CELL/schoolrail/stargazers">
    <img src="https://img.shields.io/github/stars/PGMODE-CELL/schoolrail?style=social" alt="Stars">
  </a>
  <a href="https://github.com/PGMODE-CELL/schoolrail/network/members">
    <img src="https://img.shields.io/github/forks/PGMODE-CELL/schoolrail?style=social" alt="Forks">
  </a>
</p>
