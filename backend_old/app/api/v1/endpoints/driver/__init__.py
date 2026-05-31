from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.core.security import get_current_user, UserInDB, require_driver_or_admin

router = APIRouter(prefix="/driver", tags=["Driver App"])


class DriverDashboardResponse(BaseModel):
    driver_id: int
    driver_name: str
    vehicle_id: Optional[int] = None
    vehicle_number: Optional[str] = None
    today_trips: int
    pending_students: int
    rating: float
    alerts_count: int


class TodayTripResponse(BaseModel):
    trip_id: int
    route_id: int
    route_name: str
    trip_type: str
    start_time: str
    end_time: Optional[str] = None
    status: str
    students_count: int
    stops_count: int


@router.get("/dashboard")
async def get_driver_dashboard(current_user: UserInDB = Depends(get_current_user)):
    from app.services.driver_service import get_all_drivers, get_driver_by_id
    from app.services.route_service import get_all_routes
    from app.services.gps_service import get_active_alerts
    
    drivers = get_all_drivers(status="active")
    driver = drivers[0] if drivers else None
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    routes = get_all_routes()
    driver_routes = [r for r in routes if r.driver_id == driver.id]
    
    alerts = get_active_alerts()
    driver_alerts = len([a for a in alerts if a.vehicle_id == driver.vehicle_id]) if driver.vehicle_id else 0
    
    return DriverDashboardResponse(
        driver_id=driver.id,
        driver_name=driver.first_name + " " + driver.last_name,
        vehicle_id=driver.vehicle_id,
        vehicle_number=None,
        today_trips=len(driver_routes) * 2,
        pending_students=30,
        rating=driver.rating,
        alerts_count=driver_alerts
    )


@router.get("/today-trips", response_model=List[TodayTripResponse])
async def get_today_trips(current_user: UserInDB = Depends(get_current_user)):
    from app.services.driver_service import get_all_drivers
    from app.services.route_service import get_all_routes
    
    drivers = get_all_drivers(status="active")
    driver = drivers[0] if drivers else None
    
    if not driver:
        return []
    
    routes = get_all_routes()
    driver_routes = [r for r in routes if r.driver_id == driver.id]
    
    trips = []
    for route in driver_routes:
        trips.append(TodayTripResponse(
            trip_id=route.id,
            route_id=route.id,
            route_name=route.name,
            trip_type="morning",
            start_time=route.estimated_time,
            end_time=None,
            status="scheduled",
            students_count=15,
            stops_count=len(route.stops)
        ))
        trips.append(TodayTripResponse(
            trip_id=route.id + 100,
            route_id=route.id,
            route_name=route.name,
            trip_type="evening",
            start_time="15:00",
            end_time=None,
            status="scheduled",
            students_count=15,
            stops_count=len(route.stops)
        ))
    
    return trips


@router.post("/trip/{trip_id}/start")
async def start_trip(
    trip_id: int,
    current_user: UserInDB = Depends(require_driver_or_admin)
):
    return {
        "message": "Trip started successfully",
        "trip_id": trip_id,
        "started_at": datetime.now().isoformat()
    }


@router.post("/trip/{trip_id}/end")
async def end_trip(
    trip_id: int,
    notes: Optional[str] = None,
    current_user: UserInDB = Depends(require_driver_or_admin)
):
    return {
        "message": "Trip ended successfully",
        "trip_id": trip_id,
        "ended_at": datetime.now().isoformat(),
        "total_students": 15,
        "distance_km": 12.5
    }


@router.get("/route/{route_id}/students")
async def get_route_students(
    route_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.student_service import get_students_by_route
    
    students = get_students_by_route(route_id)
    
    return {
        "route_id": route_id,
        "students": [
            {
                "id": s.id,
                "name": s.first_name + " " + s.last_name,
                "class": s.class_name,
                "section": s.section,
                "status": "not_marked"
            }
            for s in students
        ],
        "count": len(students)
    }


@router.post("/attendance/mark")
async def mark_student_attendance(
    student_id: int,
    route_id: int,
    status: str,
    trip_type: str,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.attendance_service import mark_attendance
    from app.schemas.attendance import StudentAttendanceCreate
    
    attendance = mark_attendance(StudentAttendanceCreate(
        student_id=student_id,
        route_id=route_id,
        status=status,
        pickup_time=datetime.now().strftime("%I:%M %p") if trip_type == "morning" else None,
        drop_time=datetime.now().strftime("%I:%M %p") if trip_type == "evening" else None
    ))
    
    return {
        "success": True,
        "attendance_id": attendance.id,
        "status": status
    }


@router.post("/attendance/bulk")
async def bulk_mark_attendance(
    route_id: int,
    records: List[dict],
    trip_type: str,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.attendance_service import bulk_mark_attendance
    from datetime import date
    
    student_ids = [r["student_id"] for r in records]
    statuses = {r["student_id"]: r["status"] for r in records}
    
    result = bulk_mark_attendance(student_ids, "present", date.today(), current_user.id)
    
    return {
        "success": True,
        "marked_count": result["marked_count"],
        "total": result["total"]
    }


@router.get("/vehicle/check-list")
async def get_vehicle_checklist(current_user: UserInDB = Depends(require_driver_or_admin)):
    return {
        "items": [
            {"id": 1, "name": "Fuel Level", "status": "pending"},
            {"id": 2, "name": "Tire Pressure", "status": "pending"},
            {"id": 3, "name": "Brakes", "status": "pending"},
            {"id": 4, "name": "Lights", "status": "pending"},
            {"id": 5, "name": "Mirrors", "status": "pending"},
            {"id": 6, "name": "First Aid Kit", "status": "pending"},
            {"id": 7, "name": "Fire Extinguisher", "status": "pending"},
            {"id": 8, "name": "GPS Device", "status": "pending"},
        ]
    }


@router.post("/vehicle/check-list")
async def submit_vehicle_checklist(
    checklist: List[dict],
    current_user: UserInDB = Depends(require_driver_or_admin)
):
    return {
        "message": "Vehicle checklist submitted",
        "submitted_at": datetime.now().isoformat(),
        "items_checked": len(checklist)
    }


@router.post("/vehicle/report-issue")
async def report_vehicle_issue(
    issue_type: str,
    description: str,
    severity: str = "medium",
    current_user: UserInDB = Depends(get_current_user)
):
    return {
        "message": "Issue reported successfully",
        "issue_id": 1,
        "reported_at": datetime.now().isoformat()
    }


@router.get("/alerts")
async def get_driver_alerts(current_user: UserInDB = Depends(get_current_user)):
    from app.services.gps_service import get_active_alerts
    from app.services.driver_service import get_all_drivers
    
    drivers = get_all_drivers(status="active")
    driver = drivers[0] if drivers else None
    
    alerts = get_active_alerts()
    if driver and driver.vehicle_id:
        driver_alerts = [a for a in alerts if a.vehicle_id == driver.vehicle_id]
    else:
        driver_alerts = alerts[:3]
    
    return {
        "alerts": [
            {
                "id": a.id,
                "type": a.alert_type,
                "message": a.message,
                "severity": a.severity,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in driver_alerts
        ],
        "count": len(driver_alerts)
    }
