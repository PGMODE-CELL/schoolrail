# SchoolRail Deployment Guide

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (for production)
- Docker & Docker Compose (optional)

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python main.py
```

### Admin Panel
```bash
cd admin
npm install
npm run dev
```

### Access
- Backend: http://localhost:3001
- Admin: http://localhost:3000
- API Docs: http://localhost:3001/docs

## Production Setup

### Using Docker (Recommended)

1. Clone the repository
2. Navigate to docker folder
3. Copy .env.example to .env
4. Update environment variables
5. Run:
```bash
docker-compose up -d
```

### Manual Production Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
export DEBUG=false
export DATABASE_URL=postgresql://user:pass@localhost/schoolrail
gunicorn main:app -w 4 -b 0.0.0.0:3001
```

#### Admin
```bash
cd admin
npm install
npm run build
npm start
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection | sqlite:///./schoolrail.db |
| SECRET_KEY | JWT secret key | - |
| DEBUG | Debug mode | true |
| API_URL | Backend URL | http://localhost:3001 |

## Nginx Configuration

See `docker/nginx.conf` for reverse proxy setup.

## SSL/HTTPS

Use Let's Encrypt or similar for HTTPS in production.

## Monitoring

- Set up logging with proper log rotation
- Use PM2 for process management
- Configure health checks