from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app
from redis.asyncio import Redis
from datetime import datetime

from backend.libs.shared.database import TenantRegistry, TenantSessionFactory, TenantEnginePool
from backend.libs.shared.events import EventBus

redis: Redis = None
tenant_registry: TenantRegistry = None
session_factory: TenantSessionFactory = None
engine_pool: TenantEnginePool = None
event_bus: EventBus = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis, tenant_registry, session_factory, engine_pool, event_bus
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    event_bus = EventBus("amqp://guest:guest@localhost:5672/")
    await event_bus.connect()
    tenant_registry = TenantRegistry(redis)
    engine_pool = TenantEnginePool()
    session_factory = TenantSessionFactory(tenant_registry, engine_pool)
    yield
    await event_bus.close()
    await redis.close()

app = FastAPI(title="SchoolRail Routing Service", version="1.0.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

class RouteCreate(BaseModel):
    name: str
    direction: str = "pickup"

class RouteResponse(BaseModel):
    id: str
    name: str
    direction: str
    status: str

class StopCreate(BaseModel):
    route_id: str
    name: str
    latitude: float
    longitude: float
    stop_order: int

class StopResponse(BaseModel):
    id: str
    route_id: str
    name: str
    latitude: float
    longitude: float
    stop_order: int

class TripStopEvent(BaseModel):
    trip_id: str
    stop_id: str
    vehicle_id: str
    student_count: int = 0

@app.get("/health")
async def health():
    return {"status": "ok", "service": "routing-service", "version": "1.0.0"}

@app.post("/routes", response_model=RouteResponse)
async def create_route(data: RouteCreate):
    return RouteResponse(id="00000000-0000-0000-0000-000000000000", name=data.name, direction=data.direction, status="active")

@app.get("/routes")
async def list_routes():
    return {"items": [], "total": 0}

@app.get("/routes/{route_id}")
async def get_route(route_id: str):
    return RouteResponse(id=route_id, name="", direction="pickup", status="active")

@app.put("/routes/{route_id}")
async def update_route(route_id: str, data: RouteCreate):
    return RouteResponse(id=route_id, name=data.name, direction=data.direction, status="active")

@app.delete("/routes/{route_id}")
async def delete_route(route_id: str):
    return {"status": "deleted"}

@app.post("/routes/{route_id}/optimize")
async def optimize_route(route_id: str):
    task_id = f"opt_{datetime.utcnow().timestamp()}"
    return {"task_id": task_id, "status": "queued", "route_id": route_id}

@app.get("/routes/{route_id}/optimize/{task_id}/status")
async def optimize_status(route_id: str, task_id: str):
    return {"task_id": task_id, "route_id": route_id, "status": "completed"}

@app.get("/routes/{route_id}/stops")
async def route_stops(route_id: str):
    return {"items": [], "route_id": route_id}

@app.post("/stops", response_model=StopResponse)
async def create_stop(data: StopCreate):
    return StopResponse(id="00000000-0000-0000-0000-000000000000", route_id=data.route_id, name=data.name, latitude=data.latitude, longitude=data.longitude, stop_order=data.stop_order)

@app.get("/stops/{stop_id}")
async def get_stop(stop_id: str):
    return StopResponse(id=stop_id, route_id="", name="", latitude=0.0, longitude=0.0, stop_order=0)

@app.put("/stops/{stop_id}")
async def update_stop(stop_id: str, data: StopCreate):
    return StopResponse(id=stop_id, route_id=data.route_id, name=data.name, latitude=data.latitude, longitude=data.longitude, stop_order=data.stop_order)

@app.delete("/stops/{stop_id}")
async def delete_stop(stop_id: str):
    return {"status": "deleted"}

@app.post("/trip-stops/arrive")
async def trip_stop_arrive(data: TripStopEvent):
    return {"status": "arrived", "trip_id": data.trip_id, "stop_id": data.stop_id}

@app.post("/trip-stops/depart")
async def trip_stop_depart(data: TripStopEvent):
    return {"status": "departed", "trip_id": data.trip_id, "stop_id": data.stop_id}

@app.get("/trips")
async def list_trips():
    return {"items": [], "total": 0}

@app.post("/trips")
async def create_trip():
    return {"id": "00000000-0000-0000-0000-000000000000", "status": "scheduled"}

@app.get("/trips/{trip_id}")
async def get_trip(trip_id: str):
    return {"id": trip_id, "status": "scheduled"}

@app.post("/trips/{trip_id}/start")
async def start_trip(trip_id: str):
    return {"id": trip_id, "status": "in_progress"}

@app.post("/trips/{trip_id}/complete")
async def complete_trip(trip_id: str):
    return {"id": trip_id, "status": "completed"}
