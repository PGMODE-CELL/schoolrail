# Installation Guide

## Quick Start (Docker — 5 minutes)

```bash
# Prerequisites
# - Docker Desktop 24+ (https://docker.com)
# - Git

git clone https://github.com/schoolrail/schoolrail.git
cd schoolrail
docker compose up -d
```

**Access everything**:

| Service | URL |
|---------|-----|
| Admin Panel | http://localhost:3000 |
| API Gateway | http://localhost:8000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| RabbitMQ | localhost:15672 |
| MinIO Console | localhost:9001 |
| Prometheus | localhost:9090 |
| Grafana | localhost:3001 |
| Jaeger UI | localhost:16686 |

### Included Services

| Service | Container | Port |
|---------|-----------|------|
| API Gateway | gateway | 8000 |
| Auth Service | auth-service | 8001 |
| Fleet Service | fleet-service | 8002 |
| Routing Service | routing-service | 8003 |
| Student Service | student-service | 8004 |
| Geo Service | geo-service | 8005 |
| Tenant Service | tenant-service | 8006 |
| Payment Service | payment-service | 8007 |
| Notification Service | notification-service | 8008 |
| Celery Worker | celery-worker | — |
| PostgreSQL 16 | postgres | 5432 |
| PgBouncer | pgbouncer | 6432 |
| Redis | redis | 6379 |
| RabbitMQ | rabbitmq | 5672 |
| MinIO (S3) | minio | 9000 |
| OpenTelemetry Collector | otel-collector | 4317 |
| Prometheus | prometheus | 9090 |
| Grafana | grafana | 3001 |
| Jaeger | jaeger | 16686 |
| MailHog (SMTP) | mailhog | 8025 |

---

## Production (Kubernetes)

### Prerequisites
- K8s 1.28+ cluster
- Helm 3.12+
- kubectl configured

### Deploy

```bash
cd infrastructure/helm

# Base namespace + policies
helm install schoolrail-base ./base --namespace schoolrail-production

# API Gateway
helm install api-gateway ./api-gateway --namespace schoolrail-production

# Auth Service
helm install auth-service ./auth-service --namespace schoolrail-production

# Tenant Service (with PgBouncer sidecar)
helm install tenant-service ./tenant-service --namespace schoolrail-production
```

For multi-region production: see `infrastructure/terraform/environments/production/`.

### Autoscaling

All services include HorizontalPodAutoscaler (CPU > 70% → scale up).  
Workers use spot instances. Monitoring uses on-demand small instances.

---

## Cloud Provisioning (Terraform)

```bash
cd infrastructure/terraform/environments/production
terraform init
terraform plan
terraform apply
```

Creates:
- EKS cluster with managed node groups
- RDS PostgreSQL 16 (multi-AZ, read replicas, encryption, 30-day backups)
- ElastiCache Redis Cluster (sharding, multi-AZ, encryption)
- RabbitMQ (Amazon MQ or self-hosted on EKS)
- Vault with KMS auto-unseal

---

## Manual Setup (Without Docker)

### Backend Services

Each service is independent. Run the ones you need:

```bash
# Shared dependencies
pip install fastapi uvicorn asyncpg sqlalchemy[asyncio] redis aio-pika prometheus-client

# Auth Service
cd backend/services/auth
uvicorn main:app --reload --port 8001

# Gateway
cd backend/services/gateway
uvicorn main:app --reload --port 8000
```

### Admin Panel

```bash
cd admin
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 npm run dev
```

### Mobile Apps

```bash
cd parent-app   # or driver-app
npm install
npx expo start
# Scan QR code with Expo Go app
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://schoolrail:schoolrail@localhost:5432/schoolrail` | Shared database |
| `REDIS_URL` | `redis://localhost:6379/0` | Cache + rate limiter |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:5672` | Event bus |
| `JWT_SECRET` | auto-generated | JWT signing key |
| `JWT_ALGORITHM` | `RS256` | Key algorithm |
| `VAULT_ADDR` | `http://localhost:8200` | Secrets management |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | OpenTelemetry |
| `S3_ENDPOINT` | `http://localhost:9000` | File storage |
| `S3_ACCESS_KEY` | `minioadmin` | S3 access |
| `S3_SECRET_KEY` | `minioadmin` | S3 secret |
| `SMTP_HOST` | `localhost:1025` | Email (MailHog) |

---

## Mobile Apps on Physical Devices

```bash
# Parent App
cd parent-app
npx expo start --tunnel

# Driver App
cd driver-app
npx expo start --tunnel
```

Scan the QR code with:
- **iOS**: Camera app → tap notification
- **Android**: Expo Go app → Scan QR

---

## Troubleshooting

### Docker won't start
- Ensure Docker Desktop is running
- Run `docker compose down && docker compose up -d`
- Check ports: `netstat -ano | findstr :3000`

### Database connection refused
- PostgreSQL takes ~30s to initialize on first run
- Run: `docker compose restart postgres`

### Gateway returns 503
- Microservices take a few seconds to start
- Run: `docker compose logs gateway`

### Need help?
- [GitHub Issues](https://github.com/schoolrail/schoolrail/issues)
- [Discord Community](https://discord.gg/schoolrail)
