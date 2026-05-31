# SchoolRail Docker Configuration

## Quick Start

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

## Services

- **Backend**: FastAPI on port 3001
- **Admin**: Next.js on port 3000
- **Database**: PostgreSQL on port 5432
- **Nginx**: Reverse proxy on port 80

## Environment

Copy `.env.example` to `.env` and configure:
- SECRET_KEY
- Database credentials
- API keys