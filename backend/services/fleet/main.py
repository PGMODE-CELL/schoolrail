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

@app.get("/schools")
async def list_schools():
    return {"items": [{"id": "default", "name": "Default School", "tenant_id": "default"}], "total": 1}

@app.get("/schools/{school_id}")
async def get_school(school_id: str):
    return {"id": school_id, "name": "Default School", "tenant_id": "default"}

@app.get("/schools/{school_id}/stats")
async def school_stats(school_id: str):
    return {"total_students": 0, "total_vehicles": 0, "total_drivers": 0, "total_routes": 0}

@app.post("/schools")
async def create_school():
    return {"id": "00000000-0000-0000-0000-000000000000", "name": "New School"}

@app.get("/analytics/dashboard")
async def analytics_dashboard():
    return {
        "total_vehicles": 3, "active_vehicles": 2, "total_drivers": 1,
        "total_students": 0, "total_routes": 0, "attendance_today": 0,
        "on_time_percent": 100, "alerts_active": 0,
    }

@app.get("/analytics/vehicles")
async def analytics_vehicles():
    return {"items": []}

@app.get("/analytics/routes")
async def analytics_routes():
    return {"items": []}

@app.get("/analytics/drivers")
async def analytics_drivers():
    return {"items": []}

@app.get("/analytics/attendance")
async def analytics_attendance():
    return {"items": [], "summary": {"present": 0, "absent": 0, "late": 0}}

@app.get("/analytics/fees")
async def analytics_fees():
    return {"items": [], "total_collected": 0, "total_pending": 0}

@app.get("/analytics/alerts")
async def analytics_alerts():
    return {"items": [], "total": 0}

@app.get("/reports/attendance")
async def report_attendance():
    return {"items": []}

@app.get("/reports/fees")
async def report_fees():
    return {"items": []}

@app.get("/reports/students")
async def report_students():
    return {"items": []}

@app.get("/reports/vehicles")
async def report_vehicles():
    return {"items": []}

@app.get("/drivers/{driver_id}/attendance")
async def driver_attendance(driver_id: str):
    return {"items": [], "driver_id": driver_id}

@app.get("/vehicles/{vehicle_id}/maintenance")
async def vehicle_maintenance(vehicle_id: str):
    return {"items": [], "vehicle_id": vehicle_id}
