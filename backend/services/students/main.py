from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app
from redis.asyncio import Redis

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

app = FastAPI(title="SchoolRail Student Service", version="1.0.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    grade: str = ""
    parent_id: str = ""
    pickup_address: str = ""
    dropoff_address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0

class StudentResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    grade: str
    parent_id: str
    is_active: bool

class AttendanceBatchItem(BaseModel):
    student_id: str
    status: str
    date: str

class AttendanceBatchRequest(BaseModel):
    items: list[AttendanceBatchItem]

class RidershipEvent(BaseModel):
    trip_id: str
    student_id: str
    vehicle_id: str
    latitude: float = 0.0
    longitude: float = 0.0

@app.get("/health")
async def health():
    return {"status": "ok", "service": "student-service", "version": "1.0.0"}

@app.post("/students", response_model=StudentResponse)
async def create_student(data: StudentCreate):
    return StudentResponse(
        id="00000000-0000-0000-0000-000000000000",
        first_name=data.first_name,
        last_name=data.last_name,
        grade=data.grade,
        parent_id=data.parent_id,
        is_active=True,
    )

@app.get("/students")
async def list_students():
    return {"items": [], "total": 0}

@app.get("/students/{student_id}")
async def get_student(student_id: str):
    return StudentResponse(id=student_id, first_name="", last_name="", grade="", parent_id="", is_active=True)

@app.put("/students/{student_id}")
async def update_student(student_id: str, data: StudentCreate):
    return StudentResponse(id=student_id, first_name=data.first_name, last_name=data.last_name, grade=data.grade, parent_id=data.parent_id, is_active=True)

@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    return {"status": "deleted"}

@app.post("/attendance")
async def create_attendance():
    return {"status": "ok", "id": "00000000-0000-0000-0000-000000000000"}

@app.post("/attendance/bulk")
async def bulk_attendance(data: AttendanceBatchRequest):
    return {"processed": len(data.items), "status": "ok"}

@app.get("/attendance/daily")
async def daily_attendance(date: str = ""):
    return {"items": [], "date": date}

@app.post("/ridership/check-in")
async def ridership_checkin(data: RidershipEvent):
    return {"status": "checked_in", "student_id": data.student_id, "trip_id": data.trip_id}

@app.post("/ridership/check-out")
async def ridership_checkout(data: RidershipEvent):
    return {"status": "checked_out", "student_id": data.student_id, "trip_id": data.trip_id}

@app.get("/ridership/trip/{trip_id}")
async def trip_ridership(trip_id: str):
    return {"items": [], "trip_id": trip_id}
