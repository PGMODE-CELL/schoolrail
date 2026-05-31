"""
SchoolRail - Premium Features
=============================
Ridership tracking, geofencing, field trips, maintenance scheduling, trip stop logs.
These are the features paid competitors charge extra for.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_
from typing import Optional, List
from datetime import datetime, timedelta, date
import math

from app.core.database import get_db
from app.core.security import get_current_user, TokenData
from app.models.models import (
    RidershipLog, GeofenceZone, FieldTrip, FieldTripStudent,
    MaintenanceSchedule, TripStopLog, Trip, Stop, Student,
    Vehicle, School, Attendance, Notification, GPSLocation, Alert
)
from app.schemas.schemas import (
    RidershipCheckIn, RidershipCheckOut, RidershipLogResponse, RidershipStats,
    GeofenceZoneCreate, GeofenceZoneResponse, GeofenceCheckRequest,
    FieldTripCreate, FieldTripUpdate, FieldTripResponse, FieldTripStudentAdd, FieldTripStudentResponse,
    MaintenanceScheduleCreate, MaintenanceScheduleResponse,
    TripStopLogResponse, SuccessResponse
)

router = APIRouter(prefix="/premium", tags=["Premium Features"])


# =============================================================================
# RIDERSHIP (RFID Check-in/out) - Competitors charge $1-3/student/year for this
# =============================================================================

ridership_router = APIRouter(prefix="/ridership", tags=["Ridership"])


@ridership_router.post("/check-in")
async def ridership_check_in(
    data: RidershipCheckIn,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")

    log = RidershipLog(
        school_id=student.school_id,
        student_id=data.student_id,
        vehicle_id=data.vehicle_id,
        trip_id=data.trip_id,
        stop_id=data.stop_id,
        event="check_in",
        method=data.method,
        rfid_card_id=data.rfid_card_id,
        latitude=data.latitude,
        longitude=data.longitude,
        photo_url=data.photo_url,
        notes=data.notes,
        timestamp=datetime.utcnow(),
    )
    db.add(log)

    existing = db.query(Attendance).filter(
        Attendance.student_id == data.student_id,
        Attendance.date >= datetime.utcnow().replace(hour=0, minute=0, second=0),
    ).first()
    if not existing:
        att = Attendance(
            student_id=data.student_id,
            trip_id=data.trip_id,
            date=datetime.utcnow(),
            trip_type="morning_pickup",
            status="present",
            source="rfid" if data.method == "rfid" else "manual",
            notes=f"Checked in via {data.method}",
        )
        db.add(att)

    db.commit()
    db.refresh(log)
    return {"success": True, "message": "Check-in recorded", "id": log.id}


@ridership_router.post("/check-out")
async def ridership_check_out(
    data: RidershipCheckOut,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")

    log = RidershipLog(
        school_id=student.school_id,
        student_id=data.student_id,
        vehicle_id=data.vehicle_id,
        trip_id=data.trip_id,
        stop_id=data.stop_id,
        event="check_out",
        method=data.method,
        latitude=data.latitude,
        longitude=data.longitude,
        notes=data.notes,
        timestamp=datetime.utcnow(),
    )
    db.add(log)

    existing = db.query(Attendance).filter(
        Attendance.student_id == data.student_id,
        Attendance.date >= datetime.utcnow().replace(hour=0, minute=0, second=0),
        Attendance.trip_type == "evening_drop",
    ).first()
    if not existing:
        att = Attendance(
            student_id=data.student_id,
            trip_id=data.trip_id,
            date=datetime.utcnow(),
            trip_type="evening_drop",
            status="present",
            source=log.method,
            notes=f"Checked out via {data.method}",
        )
        db.add(att)

    db.commit()
    db.refresh(log)
    return {"success": True, "message": "Check-out recorded", "id": log.id}


@ridership_router.get("/trip/{trip_id}")
async def get_trip_ridership(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    logs = db.query(RidershipLog).filter(
        RidershipLog.trip_id == trip_id
    ).order_by(RidershipLog.timestamp.desc()).all()
    return {"items": logs, "total": len(logs)}


@ridership_router.get("/stats/today")
async def get_today_ridership_stats(
    school_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
    q = db.query(RidershipLog).filter(RidershipLog.timestamp >= today_start)
    if school_id:
        q = q.filter(RidershipLog.school_id == school_id)
    if vehicle_id:
        q = q.filter(RidershipLog.vehicle_id == vehicle_id)

    logs = q.all()
    checked_in = sum(1 for l in logs if l.event == "check_in")
    checked_out = sum(1 for l in logs if l.event == "check_out")

    return RidershipStats(
        total_today=len(logs),
        checked_in=checked_in,
        checked_out=checked_out,
        on_bus=checked_in - checked_out,
    )


# =============================================================================
# GEOFENCE ZONES
# =============================================================================

geofence_router = APIRouter(prefix="/geofence", tags=["Geofence"])


@geofence_router.post("/zones")
async def create_geofence_zone(
    data: GeofenceZoneCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    zone = GeofenceZone(**data.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@geofence_router.get("/zones")
async def list_geofence_zones(
    school_id: Optional[int] = None,
    zone_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    q = db.query(GeofenceZone)
    if school_id:
        q = q.filter(GeofenceZone.school_id == school_id)
    if zone_type:
        q = q.filter(GeofenceZone.zone_type == zone_type)
    zones = q.order_by(GeofenceZone.name).all()
    return {"items": zones, "total": len(zones)}


@geofence_router.delete("/zones/{zone_id}")
async def delete_geofence_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    zone = db.query(GeofenceZone).filter(GeofenceZone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    db.delete(zone)
    db.commit()
    return SuccessResponse(success=True, message="Zone deleted")


@geofence_router.post("/check")
async def check_geofence(
    data: GeofenceCheckRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    zones = db.query(GeofenceZone).filter(GeofenceZone.is_active == True).all()
    events = []
    for zone in zones:
        d = haversine(data.latitude, data.longitude, zone.latitude, zone.longitude)
        distance_m = d * 1000
        if distance_m <= zone.radius_meters:
            events.append(GeofenceEvent(
                zone_id=zone.id, zone_name=zone.name, zone_type=zone.zone_type,
                vehicle_id=data.vehicle_id, event="entered", distance_meters=round(distance_m, 1),
            ).model_dump())

            if zone.notify_parents:
                alert = Alert(
                    school_id=zone.school_id, vehicle_id=data.vehicle_id,
                    alert_type="geofence_entry", title=f"Bus entering {zone.name}",
                    message=f"Vehicle has entered zone: {zone.name}",
                    severity="info", latitude=data.latitude, longitude=data.longitude,
                )
                db.add(alert)

    db.commit()
    return {"events": events, "count": len(events)}


# =============================================================================
# FIELD TRIPS
# =============================================================================

field_trip_router = APIRouter(prefix="/field-trips", tags=["Field Trips"])


@field_trip_router.post("")
async def create_field_trip(
    data: FieldTripCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    student_ids = data.student_ids or []
    trip_data = data.model_dump(exclude={"student_ids"})
    ft = FieldTrip(**trip_data)
    db.add(ft)
    db.flush()

    for sid in student_ids:
        fts = FieldTripStudent(field_trip_id=ft.id, student_id=sid)
        db.add(fts)

    ft.total_students = len(student_ids)
    db.commit()
    db.refresh(ft)
    return ft


@field_trip_router.get("")
async def list_field_trips(
    school_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    q = db.query(FieldTrip)
    if school_id:
        q = q.filter(FieldTrip.school_id == school_id)
    if status:
        q = q.filter(FieldTrip.status == status)
    trips = q.order_by(desc(FieldTrip.departure_datetime)).all()
    return {"items": trips, "total": len(trips)}


@field_trip_router.get("/{trip_id}")
async def get_field_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    ft = db.query(FieldTrip).filter(FieldTrip.id == trip_id).first()
    if not ft:
        raise HTTPException(404, "Field trip not found")
    students = db.query(FieldTripStudent).filter(
        FieldTripStudent.field_trip_id == trip_id
    ).all()
    result = ft.__dict__
    result["students"] = [
        {
            "id": s.id, "student_id": s.student_id, "checked_in": s.checked_in,
            "checked_out": s.checked_out, "permission_slip_received": s.permission_slip_received,
        }
        for s in students
    ]
    return result


@field_trip_router.post("/{trip_id}/students")
async def add_students_to_field_trip(
    trip_id: int,
    data: FieldTripStudentAdd,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    ft = db.query(FieldTrip).filter(FieldTrip.id == trip_id).first()
    if not ft:
        raise HTTPException(404, "Field trip not found")
    for sid in data.student_ids:
        exists = db.query(FieldTripStudent).filter(
            FieldTripStudent.field_trip_id == trip_id,
            FieldTripStudent.student_id == sid,
        ).first()
        if not exists:
            db.add(FieldTripStudent(field_trip_id=trip_id, student_id=sid))
    ft.total_students = db.query(FieldTripStudent).filter(
        FieldTripStudent.field_trip_id == trip_id
    ).count()
    db.commit()
    return {"success": True, "message": f"{len(data.student_ids)} students added"}


@field_trip_router.post("/{trip_id}/check-in/{student_id}")
async def field_trip_check_in(
    trip_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    fts = db.query(FieldTripStudent).filter(
        FieldTripStudent.field_trip_id == trip_id,
        FieldTripStudent.student_id == student_id,
    ).first()
    if not fts:
        raise HTTPException(404, "Student not in this field trip")
    fts.checked_in = True
    fts.checked_in_time = datetime.utcnow()

    ft = db.query(FieldTrip).filter(FieldTrip.id == trip_id).first()
    ft.checked_in_count = db.query(FieldTripStudent).filter(
        FieldTripStudent.field_trip_id == trip_id,
        FieldTripStudent.checked_in == True,
    ).count()

    db.commit()
    return {"success": True, "message": "Student checked in for field trip"}


@field_trip_router.post("/{trip_id}/check-out/{student_id}")
async def field_trip_check_out(
    trip_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    fts = db.query(FieldTripStudent).filter(
        FieldTripStudent.field_trip_id == trip_id,
        FieldTripStudent.student_id == student_id,
    ).first()
    if not fts:
        raise HTTPException(404, "Student not in this field trip")
    fts.checked_out = True
    fts.checked_out_time = datetime.utcnow()

    ft = db.query(FieldTrip).filter(FieldTrip.id == trip_id).first()
    ft.checked_out_count = db.query(FieldTripStudent).filter(
        FieldTripStudent.field_trip_id == trip_id,
        FieldTripStudent.checked_out == True,
    ).count()

    db.commit()
    return {"success": True, "message": "Student checked out from field trip"}


# =============================================================================
# MAINTENANCE SCHEDULING
# =============================================================================

maintenance_router = APIRouter(prefix="/maintenance-schedule", tags=["Maintenance Schedule"])


@maintenance_router.post("/schedules")
async def create_maintenance_schedule(
    data: MaintenanceScheduleCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")

    sched = MaintenanceSchedule(
        vehicle_id=data.vehicle_id,
        task_name=data.task_name,
        description=data.description,
        maintenance_type=data.maintenance_type,
        interval_km=data.interval_km,
        interval_days=data.interval_days,
        last_done_km=data.last_done_km,
        next_due_km=data.last_done_km + data.interval_km if data.last_done_km else data.interval_km,
        estimated_cost=data.estimated_cost,
        assigned_to=data.assigned_to,
    )
    if vehicle.last_service_date:
        sched.next_due_date = vehicle.last_service_date + timedelta(days=data.interval_days)
    else:
        sched.next_due_date = datetime.utcnow() + timedelta(days=data.interval_days)

    db.add(sched)
    db.commit()
    db.refresh(sched)
    return sched


@maintenance_router.get("/schedules")
async def list_maintenance_schedules(
    vehicle_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    q = db.query(MaintenanceSchedule)
    if vehicle_id:
        q = q.filter(MaintenanceSchedule.vehicle_id == vehicle_id)
    if is_active is not None:
        q = q.filter(MaintenanceSchedule.is_active == is_active)
    schedules = q.order_by(MaintenanceSchedule.next_due_date).all()
    return {"items": schedules, "total": len(schedules)}


@maintenance_router.get("/upcoming")
async def get_upcoming_maintenance(
    days: int = Query(30, ge=1),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    cutoff = datetime.utcnow() + timedelta(days=days)
    schedules = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.is_active == True,
        MaintenanceSchedule.next_due_date <= cutoff,
    ).order_by(MaintenanceSchedule.next_due_date).all()
    return {"items": schedules, "total": len(schedules), "within_days": days}


@maintenance_router.post("/schedules/{schedule_id}/complete")
async def complete_maintenance_task(
    schedule_id: int,
    completed_km: Optional[float] = None,
    cost: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    sched = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()
    if not sched:
        raise HTTPException(404, "Schedule not found")

    now = datetime.utcnow()
    sched.last_done_date = now
    sched.last_done_km = completed_km or sched.next_due_km or 0
    sched.next_due_km = sched.last_done_km + sched.interval_km
    sched.next_due_date = now + timedelta(days=sched.interval_days)
    if cost:
        sched.estimated_cost = cost

    vehicle = db.query(Vehicle).filter(Vehicle.id == sched.vehicle_id).first()
    if vehicle:
        vehicle.last_service_date = now

    db.commit()
    return {"success": True, "message": f"Maintenance '{sched.task_name}' completed"}


# =============================================================================
# TRIP STOP LOGS (live stop-by-stop tracking)
# =============================================================================

trip_stops_router = APIRouter(prefix="/trip-stops", tags=["Trip Stops"])


@trip_stops_router.post("/{trip_id}/arrive/{stop_id}")
async def record_stop_arrival(
    trip_id: int,
    stop_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    stop = db.query(Stop).filter(Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(404, "Stop not found")

    log = db.query(TripStopLog).filter(
        TripStopLog.trip_id == trip_id,
        TripStopLog.stop_id == stop_id,
    ).first()
    if not log:
        log = TripStopLog(
            trip_id=trip_id, stop_id=stop_id,
            stop_order=stop.stop_order,
        )
        db.add(log)

    log.arrived_at = datetime.utcnow()
    log.status = "arrived"

    if log.departed_at:
        delay = (log.arrived_at - log.departed_at).total_seconds() / 60
        log.delay_minutes = max(0, int(delay - stop.pickup_time_to.replace(',', ':').split(':')[0]) if stop.pickup_time_to else 0)
        log.delay_minutes = max(0, int(delay - 5))

    db.commit()
    db.refresh(log)
    return {"success": True, "message": f"Arrived at {stop.name}", "log": {
        "id": log.id, "stop_id": stop_id, "arrived_at": str(log.arrived_at),
    }}


@trip_stops_router.post("/{trip_id}/depart/{stop_id}")
async def record_stop_departure(
    trip_id: int,
    stop_id: int,
    students_boarded: int = 0,
    students_alighted: int = 0,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    log = db.query(TripStopLog).filter(
        TripStopLog.trip_id == trip_id,
        TripStopLog.stop_id == stop_id,
    ).first()
    if not log:
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        stop = db.query(Stop).filter(Stop.id == stop_id).first()
        if not trip or not stop:
            raise HTTPException(404, "Trip or Stop not found")
        log = TripStopLog(
            trip_id=trip_id, stop_id=stop_id,
            stop_order=stop.stop_order,
        )
        db.add(log)

    log.departed_at = datetime.utcnow()
    log.students_boarded = students_boarded
    log.students_alighted = students_alighted
    log.status = "departed"

    db.commit()
    return {"success": True, "message": f"Departed from stop"}


@trip_stops_router.get("/{trip_id}")
async def get_trip_stop_logs(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    logs = db.query(TripStopLog).filter(
        TripStopLog.trip_id == trip_id
    ).order_by(TripStopLog.stop_order).all()
    return {"items": logs, "total": len(logs)}


# =============================================================================
# ROUTE OPTIMIZATION
# =============================================================================

@router.post("/routes/{route_id}/optimize")
async def optimize_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Reorder stops using nearest-neighbor heuristic (shortest path)"""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(404, "Route not found")

    stops = db.query(Stop).filter(
        Stop.route_id == route_id,
        Stop.is_active == True,
    ).order_by(Stop.stop_order).all()

    if len(stops) < 2:
        raise HTTPException(400, "Need at least 2 stops to optimize")

    optimized = nearest_neighbor_optimize(stops)

    for i, stop in enumerate(optimized):
        stop.stop_order = i + 1

    db.commit()
    return {
        "success": True,
        "message": f"Route optimized: {len(optimized)} stops reordered",
        "original_distance_km": route.total_distance_km,
        "optimized_stops": [
            {"id": s.id, "name": s.name, "order": s.stop_order}
            for s in optimized
        ],
    }


def haversine(lat1, lon1, lat2, lon2):
    """Haversine distance in km"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def nearest_neighbor_optimize(stops):
    """Nearest-neighbor TSP heuristic for stop ordering"""
    remaining = list(stops)
    if not remaining:
        return []
    path = [remaining.pop(0)]
    while remaining:
        last = path[-1]
        nearest = min(remaining, key=lambda s: haversine(
            last.latitude, last.longitude, s.latitude, s.longitude
        ))
        path.append(nearest)
        remaining.remove(nearest)
    return path


# =============================================================================
# EMERGENCY BROADCAST
# =============================================================================

@router.post("/alerts/broadcast")
async def broadcast_emergency_alert(
    title: str,
    message: str,
    severity: str = "high",
    school_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Broadcast an emergency alert to all users in a school"""
    q = db.query(Alert)
    if school_id:
        q = q.filter(Alert.school_id == school_id)

    alert = Alert(
        school_id=school_id or 1,
        alert_type="emergency_broadcast",
        title=title,
        message=message,
        severity=severity,
    )
    db.add(alert)

    from app.models.models import User, Notification
    users = db.query(User).filter(
        User.school_id == school_id if school_id else True,
        User.is_active == True,
    ).all()

    for user in users:
        notif = Notification(
            school_id=school_id or 1,
            user_id=user.id,
            notification_type="push",
            title=f"🚨 {title}",
            message=message,
            delivery_status="sent",
            sent_at=datetime.utcnow(),
        )
        db.add(notif)

    db.commit()
    return {
        "success": True,
        "message": f"Emergency alert broadcast to {len(users)} users",
        "alert_id": alert.id,
    }
