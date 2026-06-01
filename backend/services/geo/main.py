from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app
from redis.asyncio import Redis
from datetime import datetime
import json
import asyncio

from backend.libs.shared.database import TenantRegistry, TenantSessionFactory, TenantEnginePool

redis: Redis = None
tenant_registry: TenantRegistry = None
session_factory: TenantSessionFactory = None
engine_pool: TenantEnginePool = None

active_connections: dict[str, list[WebSocket]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis, tenant_registry, session_factory, engine_pool
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    tenant_registry = TenantRegistry(redis)
    engine_pool = TenantEnginePool()
    session_factory = TenantSessionFactory(tenant_registry, engine_pool)
    yield
    await redis.close()

app = FastAPI(title="SchoolRail Geo Service", version="1.0.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

class PositionUpdate(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    speed: float = 0.0
    heading: float = 0.0
    timestamp: str = ""

class GeofenceZoneCreate(BaseModel):
    name: str
    zone_type: str
    coordinates: list
    radius_meters: float = 0.0

class GeofenceCheck(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float

@app.get("/health")
async def health():
    return {"status": "ok", "service": "geo-service", "version": "1.0.0"}

@app.post("/geo/position")
async def push_position(data: PositionUpdate):
    ts = data.timestamp or datetime.utcnow().isoformat()
    payload = {
        "vehicle_id": data.vehicle_id,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "speed": data.speed,
        "heading": data.heading,
        "timestamp": ts,
    }
    await redis.setex(f"pos:{data.vehicle_id}", 30, json.dumps(payload))
    ws_list = active_connections.get(data.vehicle_id, [])
    dead = []
    for ws in ws_list:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        ws_list.remove(ws)
    return {"status": "ok"}

@app.get("/geo/vehicle/{vehicle_id}/live")
async def live_position(vehicle_id: str):
    data = await redis.get(f"pos:{vehicle_id}")
    if not data:
        raise HTTPException(status_code=404, detail={"code": "NO_POSITION", "message": "No position data available"})
    return json.loads(data)

@app.websocket("/ws")
async def websocket_ping(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({"type": "pong", "data": data}))
    except WebSocketDisconnect:
        pass

@app.websocket("/geo/vehicle/{vehicle_id}/stream")
async def position_stream(websocket: WebSocket, vehicle_id: str):
    await websocket.accept()
    if vehicle_id not in active_connections:
        active_connections[vehicle_id] = []
    active_connections[vehicle_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await redis.setex(f"pos:{vehicle_id}", 30, data)
            ws_list = active_connections.get(vehicle_id, [])
            for ws in ws_list:
                if ws != websocket:
                    try:
                        await ws.send_text(data)
                    except Exception:
                        pass
    except WebSocketDisconnect:
        if vehicle_id in active_connections:
            active_connections[vehicle_id].remove(websocket)

@app.post("/geo/geofence/zones", response_model=dict)
async def create_geofence(data: GeofenceZoneCreate):
    return {"status": "created", "name": data.name, "zone_type": data.zone_type}

@app.get("/geo/geofence/zones")
async def list_geofences():
    return {"items": []}

@app.post("/geo/geofence/check")
async def check_geofence(data: GeofenceCheck):
    return {"vehicle_id": data.vehicle_id, "in_zones": [], "alerts": []}

@app.get("/geo/proximity-alerts")
async def proximity_alerts():
    return {"items": []}

@app.post("/gps/location")
async def gps_location():
    return {"status": "ok"}

@app.get("/gps/active")
async def gps_active():
    return {"items": []}

@app.get("/gps/vehicle/{vehicle_id}")
async def gps_vehicle(vehicle_id: str):
    return {"vehicle_id": vehicle_id, "latitude": 0, "longitude": 0, "speed": 0}

@app.get("/gps/vehicle/{vehicle_id}/history")
async def gps_vehicle_history(vehicle_id: str):
    return {"items": [], "vehicle_id": vehicle_id}
