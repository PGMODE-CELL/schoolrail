from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app
from redis.asyncio import Redis
from sqlalchemy import text

from backend.libs.shared.database import TenantRegistry, TenantSessionFactory, TenantEnginePool

redis: Redis = None
tenant_registry: TenantRegistry = None
session_factory: TenantSessionFactory = None
engine_pool: TenantEnginePool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis, tenant_registry, session_factory, engine_pool
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    tenant_registry = TenantRegistry(redis)
    engine_pool = TenantEnginePool()
    session_factory = TenantSessionFactory(tenant_registry, engine_pool)
    yield
    await redis.close()

app = FastAPI(title="SchoolRail Fleet Service", version="1.0.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

class VehicleCreate(BaseModel):
    plate_number: str
    make: str = ""
    model: str = ""
    year: int = 0
    capacity: int

class VehicleResponse(BaseModel):
    id: str
    plate_number: str
    make: str
    model: str
    year: int
    capacity: int
    status: str

class DriverCreate(BaseModel):
    user_id: str
    license_number: str
    phone: str = ""

class DriverResponse(BaseModel):
    id: str
    user_id: str
    license_number: str
    phone: str
    status: str

class MaintenanceCreate(BaseModel):
    vehicle_id: str
    maintenance_type: str
    scheduled_date: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "fleet-service", "version": "1.0.0"}

@app.post("/vehicles", response_model=VehicleResponse)
async def create_vehicle(data: VehicleCreate):
    return VehicleResponse(
        id="00000000-0000-0000-0000-000000000000",
        plate_number=data.plate_number,
        make=data.make,
        model=data.model,
        year=data.year,
        capacity=data.capacity,
        status="active",
    )

@app.get("/vehicles")
async def list_vehicles():
    return {"items": [], "total": 0}

@app.get("/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str):
    return VehicleResponse(id=vehicle_id, plate_number="", make="", model="", year=0, capacity=0, status="active")

@app.put("/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: str, data: VehicleCreate):
    return VehicleResponse(id=vehicle_id, plate_number=data.plate_number, make=data.make, model=data.model, year=data.year, capacity=data.capacity, status="active")

@app.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str):
    return {"status": "deleted"}

@app.get("/vehicles/{vehicle_id}/maintenance-history")
async def vehicle_maintenance_history(vehicle_id: str):
    return {"items": [], "vehicle_id": vehicle_id}

@app.post("/vehicles/{vehicle_id}/assign-driver")
async def assign_driver(vehicle_id: str, driver_id: str):
    return {"status": "assigned", "vehicle_id": vehicle_id, "driver_id": driver_id}

@app.post("/drivers", response_model=DriverResponse)
async def create_driver(data: DriverCreate):
    return DriverResponse(id="00000000-0000-0000-0000-000000000000", user_id=data.user_id, license_number=data.license_number, phone=data.phone, status="available")

@app.get("/drivers")
async def list_drivers():
    return {"items": [], "total": 0}

@app.get("/drivers/{driver_id}")
async def get_driver(driver_id: str):
    return DriverResponse(id=driver_id, user_id="", license_number="", phone="", status="available")

@app.get("/drivers/{driver_id}/routes")
async def driver_routes(driver_id: str):
    return {"items": [], "driver_id": driver_id}

@app.post("/maintenance/schedule")
async def schedule_maintenance(data: MaintenanceCreate):
    return {"status": "scheduled", "vehicle_id": data.vehicle_id, "maintenance_type": data.maintenance_type}

@app.get("/maintenance/upcoming")
async def upcoming_maintenance():
    return {"items": []}
