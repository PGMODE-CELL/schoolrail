# SchoolRail System Requirements

## Minimum Requirements

### Backend (Python)
- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (optional for caching)

### Frontend (Next.js)
- Node.js 18+
- npm 9+

### Mobile Apps (React Native)
- Node.js 18+
- Expo SDK 50+
- Android Studio / Xcode (for building)

## Running with Docker (Recommended)

```bash
# Install Docker Desktop
# Start Docker

# Clone and run
cd schoolrail
docker-compose up --build

# Access:
# - Admin: http://localhost:3000
# - API: http://localhost:3001
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

## Manual Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd admin
npm install
npm run dev
```

### Mobile
```bash
# Parent App
cd parent-app
npm install
npx expo start

# Driver App
cd driver-app
npm install
npx expo start
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- Database URL
- Redis URL
- API keys (SMS, Email, Maps, Payment)

## Default Login
- Admin: admin@schoolrail.com / admin123
- Driver: driver1@schoolrail.com / admin123
- Parent: parent1@schoolrail.com / admin123