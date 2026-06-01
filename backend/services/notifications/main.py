from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="SchoolRail Notification Service", version="1.0.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification-service", "version": "1.0.0"}

@app.get("/notifications")
async def list_notifications():
    return {"items": [], "total": 0}

@app.post("/notifications")
async def send_notification():
    return {"status": "sent", "id": "00000000-0000-0000-0000-000000000000"}

@app.get("/alerts")
async def list_alerts():
    return {"items": [], "total": 0}

@app.post("/alerts")
async def create_alert():
    return {"id": "00000000-0000-0000-0000-000000000000", "status": "active"}

@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    return {"id": alert_id, "status": "active"}

@app.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    return {"id": alert_id, "status": "read"}

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    return {"id": alert_id, "status": "resolved"}
