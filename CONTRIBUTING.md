# Contributing to SchoolRail

Thank you for considering contributing to SchoolRail — the free, open-source alternative to expensive school transportation software.

> **Every contribution matters.** Code, docs, translations, design, bug reports, feature requests — all welcome.

---

## Quick Start for Contributors

```bash
# Fork + clone
git clone https://github.com/YOUR_USERNAME/schoolrail.git
cd schoolrail

# Start all services
docker compose up -d

# Admin: http://localhost:3000
# API Gateway: http://localhost:8000
# Grafana: http://localhost:3001

# Register an admin account at http://localhost:3000
```

---

## Development Workflow

### 1. Pick an Issue

- [Good first issues](https://github.com/schoolrail/schoolrail/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- [Help wanted](https://github.com/schoolrail/schoolrail/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
- Or open a new issue to discuss your idea

### 2. Branch

```bash
git checkout -b feat/your-feature-name
# or fix/your-bugfix-name
```

### 3. Develop

**Backend (Python/FastAPI)** — edit a specific service:

```bash
cd backend/services/auth      # or fleet, routing, students, geo, tenant, gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 4001
```

**Admin Panel (Next.js)**:

```bash
cd admin
npm install
npm run dev
```

**Mobile Apps (React Native)**:

```bash
cd parent-app   # or driver-app
npm install
npx expo start
```

**Async Workers**:

```bash
cd backend/workers
celery -A celery_app worker -Q optimization,reports,notifications,sync -l info
```

### 4. Test

```bash
# Backend tests
cd backend/services/auth
pytest tests/ -v

# Admin typecheck
cd admin
npx tsc --noEmit

# Lint
npm run lint           # root
cd admin && npm run lint   # admin
```

### 5. Commit

```bash
git add -A
git commit -m "feat: add attendance bulk marking endpoint"
git push origin feat/your-feature-name
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Usage |
|--------|-------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `refactor:` | Code restructuring |
| `perf:` | Performance improvement |
| `test:` | Adding/fixing tests |
| `chore:` | Build, CI, dependencies |
| `infra:` | Infrastructure (Terraform, Helm, K8s) |

### 6. Open a Pull Request

Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md).  
A maintainer will review within 48 hours.

---

## Code Style

| Language | Standard | Check |
|----------|----------|-------|
| Python | PEP 8 + Ruff | `ruff check --fix` |
| TypeScript | Prettier + ESLint | `npm run lint` |
| YAML/HCL | 2-space indent | Lint in CI |
| Shell | ShellCheck | Lint in CI |

**No commented-out code.** Delete it. Git history has it.

---

## Architecture Overview

```
schoolrail/
├── backend/libs/shared/       # Multi-tenant DB router, event bus, JWT, rate limiter
├── backend/services/          # 8 microservices (gateway, auth, fleet, routing, students, geo, tenant, payments)
├── backend/workers/           # Celery async workers
├── admin/                     # Next.js admin panel
├── parent-app/                # Offline-first parent mobile app
├── driver-app/                # Offline-first driver mobile app
├── infrastructure/            # Terraform, Helm, K8s, CI/CD
└── docker-compose.yml         # Local dev (16 services)
```

Key architectural decisions:
- **Database-per-tenant** for isolation. No shared tables across schools.
- **Async communication** via RabbitMQ for non-critical paths.
- **Offline-first** mobile — work without internet, sync on reconnect.
- **OpenTelemetry** everywhere — every service exports traces + metrics.

For details, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Adding a New Microservice

1. Create `backend/services/your-service/main.py` with FastAPI app
2. Add `/health` and `/metrics` endpoints
3. Add to `backend/services/gateway/routes.py`
4. Add Dockerfile + Helm chart in `infrastructure/`
5. Add service in `docker-compose.yml`
6. Document endpoints in `docs/API.md`

---

## Reporting Issues

| Type | Template | Response Time |
|------|----------|---------------|
| 🐛 Bug | [bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md) | < 48 hours |
| ✨ Feature | [feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md) | < 1 week |
| 🔒 Security | [SECURITY.md](SECURITY.md) | < 24 hours |

---

## Recognition

Contributors get:
- Name in the project README
- Say in roadmap decisions
- Priority review for future PRs
- Sticker pack (for significant contributions)

---

## License

By contributing, you agree your contributions will be licensed under [MIT](LICENSE).
