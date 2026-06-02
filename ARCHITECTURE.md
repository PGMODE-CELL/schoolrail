# SchoolRail Platform Architecture

## Design Tenets
- **Tenant isolation**: Database-per-tenant with connection pooling via PgBouncer
- **Microservices**: Loosely coupled, event-driven, independently deployable
- **Async-first**: All non-critical paths delegated to workers via RabbitMQ
- **Offline-first**: Mobile apps work without connectivity, sync via background workers
- **Observability by default**: Every service exports OpenTelemetry traces + Prometheus metrics

## Service Map

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Admin Web  │    │  Parent App  │    │  Driver App  │
│  (Next.js)   │    │  (RN Native) │    │  (RN Native) │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
              ┌────────────▼────────────┐
               │     API Gateway         │
               │ (FastAPI proxy)         │
               │  Rate limit | Auth |    │
               │  Tenant resolution      │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────┐
              │   Tenant Router     │
              │  (service mesh)     │
              └──┬──────┬──────┬────┘
                 │      │      │
    ┌────────────┘      │      └────────────┐
    ▼                   ▼                   ▼
┌──────────┐     ┌──────────┐       ┌──────────┐
│ Auth     │     │ Fleet    │       │ Routing  │
│ Service  │◄───►│ Service  │◄─────►│ Service  │
│  :8001   │     │  :8002   │       │  :8003   │
└────┬─────┘     └────┬─────┘       └────┬─────┘
     │                │                  │
     ▼                ▼                  ▼
┌──────────┐     ┌──────────┐       ┌──────────┐
│ Student  │     │ Geo      │       │ Tenant   │
│ Service  │◄───►│ Service  │       │ Service  │
│  :8004   │     │  :8005   │       │  :8006   │
└────┬─────┘     └────┬─────┘       └────┬─────┘
     │                │                  │
     └────────────────┼──────────────────┘
                      │
              ┌───────▼────────┐
              │  Event Bus     │
              │  (RabbitMQ)    │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │  Workers       │
              │  - Route Opt   │
              │  - Reports     │
              │  - Notify      │
              │  - Sync        │
              └────────────────┘

## Data Layer

┌─────────────────────────────────────────┐
│            Shared PostgreSQL            │
│  (Citus distributed)                    │
│  Tables: tenants, users, global_configs │
└────────────┬────────────────────────────┘
             │
    ┌────────▼────────┐
    │  Tenant Router  │
    │  (per-request)  │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Tenant DB Pool │
    │  (PgBouncer)    │
    │  db_tenant_XXXX │
    └─────────────────┘

## Technology Stack

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| API Gateway        | FastAPI proxy + middleware          |
| Service Mesh       | Envoy / Istio                       |
| Services           | Python FastAPI / Go (geo)           |
| Async Workers      | Celery + Redis + RabbitMQ           |
| Database           | PostgreSQL 16 + Citus + PgBouncer   |
| Cache              | Redis Cluster                       |
| File Storage       | MinIO / S3                          |
| Real-time          | WebSocket (Socket.IO)               |
| Tracing            | OpenTelemetry → Jaeger              |
| Metrics            | Prometheus → Grafana                |
| Logs               | JSON structured → Loki              |
| Container          | Docker + K8s + Helm                 |
| Provisioning       | Terraform + Crossplane              |
| GitOps             | ArgoCD                              |
| Secrets            | HashiCorp Vault                     |
| CI/CD              | GitHub Actions                      |
| Monitoring         | PagerDuty + Sentry                  |

## Tenant Resolution Flow

1. Request hits API Gateway
2. Gateway extracts `X-Tenant-ID` header or subdomain (schoolname.example.com)
3. Gateway calls Tenant Service to validate + get DB connection string
4. Request forwarded to target service with tenant context injected
5. Service uses tenant-specific DB pool from PgBouncer
6. Response returned through gateway

## Event-Driven Communication

All services communicate asynchronously via RabbitMQ for non-critical paths:

- `student.attendance.updated` → triggers notification + analytics
- `route.optimization.requested` → async route optimizer worker
- `payment.completed` → triggers receipt + balance update
- `geo.position.updated` → updates live tracking + geofence checks
- `maintenance.due` → pushes notification to driver + admin
- `emergency.alert` → broadcasts to all users in school

Synchronous calls (gRPC or HTTP) only for read-heavy, latency-sensitive paths:
- Get student details for attendance marking
- Get vehicle location for live tracking
- Get route stops for navigation

## Multi-Region Deployment

```
┌────────────────────────────────────────────┐
│          Global Load Balancer              │
│          (AWS Global Accelerator)          │
└────────────┬───────────────┬──────────────┘
             │               │
    ┌────────▼────────┐     │
    │  Region: us-east │     │
    │  ┌─────────────┐ │     │
    │  │ K8s Cluster │ │     │
    │  │ Services    │ │     │
    │  │ DB Primary  │ │     │
    │  └─────────────┘ │     │
    └─────────────────┘     │
                            │
                    ┌───────▼──────────┐
                    │  Region: eu-west │
                    │  ┌─────────────┐ │
                    │  │ K8s Cluster │ │
                    │  │ Services    │ │
                    │  │ DB Replica  │ │
                    │  └─────────────┘ │
                    └─────────────────┘
```

## Offline-First Mobile Sync

```
┌─────────────────────────────────────┐
│          Mobile Device              │
│  ┌───────────────────────────────┐  │
│  │  WatermelonDB (local SQLite)  │  │
│  │  - Students list             │  │
│  │  - Routes cache              │  │
│  │  - Pending attendance        │  │
│  │  - Pending GPS logs          │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  Sync Engine (background)     │  │
│  │  - Pull: GET /sync/changes    │  │
│  │  - Push: POST /sync/batch     │  │
│  │  - Conflict resolution: LWW   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Scaling Dimensions

| Dimension            | Strategy                                |
|-----------------------|-----------------------------------------|
| 1-10 schools          | Single DB, shared tables                |
| 10-1,000 schools      | Database-per-tenant, read replicas      |
| 1,000-100k schools    | Sharded tenant registry, Citus, caching |
| 100k-1M schools       | Multi-region, tenant sharding, CDN      |
| 1M+ schools           | Custom partitioning, geo-replication    |

## Security Architecture

- **Auth**: JWT with rotating keys (RS256), OAuth 2.0 + OpenID Connect
- **Tenant isolation**: Row-level security + separate DB connections
- **Rate limiting**: Per-tenant, per-endpoint, sliding window (Redis)
- **Audit log**: Immutable, all mutations logged with user/tenant/timestamp
- **Encryption**: AES-256 at rest (DB + S3), TLS 1.3 in transit
- **Secrets**: Vault with dynamic DB credentials, auto-rotation
- **DDoS**: Cloudflare + WAF + rate limiting at gateway
