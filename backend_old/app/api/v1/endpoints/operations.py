"""
SchoolRail - Trips, Alerts, Maintenance Endpoints
====================================================
Additional API endpoints for trips, alerts, and maintenance.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import desc, func, and_

from app.core.database import get_db
from app.core.security import get_current_user, TokenData
from app.models.models import Trip, Alert, MaintenanceRecord, Vehicle, Driver, Route, Student, GPSLocation
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class TripStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripType(str, Enum):
    MORNING_PICKUP = "morning_pickup"
    EVENING_DROP = "evening_drop"


class TripCreate(BaseModel):
    school_id: int
    vehicle_id: int
    driver_id: Optional[int] = None
    route_id: int
    trip_type: TripType
    scheduled_start_time: datetime
    scheduled_end_time: Optional[datetime] = None
    notes: Optional[str] = None


class TripUpdate(BaseModel):
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    start_odometer: Optional[float] = None
    end_odometer: Optional[float] = None
    distance_km: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AlertCreate(BaseModel):
    school_id: int
    alert_type: str
    title: str
    message: str
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    student_id: Optional[int] = None
    route_id: Optional[int] = None
    severity: str = "medium"


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class MaintenanceCreate(BaseModel):
    vehicle_id: int
    maintenance_type: str
    title: str
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    odometer_reading: Optional[float] = None
    cost: Optional[float] = None
    vendor_name: Optional[str] = None
    vendor_phone: Optional[str] = None
    parts_replaced: Optional[str] = None
    next_due_date: Optional[datetime] = None
    next_due_km: Optional[float] = None


class GPSLocationCreate(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed_kmh: Optional[float] = None
    direction: Optional[float] = None
    accuracy: Optional[float] = None
    provider: Optional[str] = None


# =============================================================================
# TRIPS ROUTER
# =============================================================================

trips_router = APIRouter(prefix="/trips", tags=["Trips"])


@trips_router.get("")
async def get_trips(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    school_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    status: Optional[str] = None,
    trip_type: Optional[str] = None,
    date: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all trips."""
    query_school_id = school_id or current_user.school_id
    if not query_school_id:
        raise HTTPException(status_code=400, detail="School ID required")
    
    query = db.query(Trip).filter(Trip.school_id == query_school_id)
    
    if vehicle_id:
        query = query.filter(Trip.vehicle_id == vehicle_id)
    if driver_id:
        query = query.filter(Trip.driver_id == driver_id)
    if status:
        query = query.filter(Trip.status == status)
    if trip_type:
        query = query.filter(Trip.trip_type == trip_type)
    if date:
        query = query.filter(func.date(Trip.scheduled_start_time) == date)
    
    total = query.count()
    trips = query.order_by(desc(Trip.scheduled_start_time)).offset((page - 1) * limit).limit(limit).all()
    return {"items": trips, "total": total, "page": page, "limit": limit}


@trips_router.get("/{trip_id}")
async def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get trip by ID."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@trips_router.post("", status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new trip."""
    trip = Trip(**trip_data.dict(), status="scheduled", students_count=0)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@trips_router.put("/{trip_id}")
async def update_trip(
    trip_id: int,
    trip_data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    for key, value in trip_data.dict(exclude_unset=True).items():
        setattr(trip, key, value)
    
    db.commit()
    db.refresh(trip)
    return trip


@trips_router.post("/{trip_id}/start")
async def start_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Start a trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.status != "scheduled":
        raise HTTPException(status_code=400, detail="Trip cannot be started")
    
    trip.status = "ongoing"
    trip.actual_start_time = datetime.utcnow()
    db.commit()
    
    return {"message": "Trip started", "trip": trip}


@trips_router.post("/{trip_id}/complete")
async def complete_trip(
    trip_id: int,
    end_odometer: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Complete a trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.status != "ongoing":
        raise HTTPException(status_code=400, detail="Trip is not ongoing")
    
    trip.status = "completed"
    trip.actual_end_time = datetime.utcnow()
    
    if end_odometer and trip.start_odometer:
        trip.distance_km = end_odometer - trip.start_odometer
    
    db.commit()
    
    return {"message": "Trip completed", "trip": trip}


@trips_router.delete("/{trip_id}")
async def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete/cancel trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip.status = "cancelled"
    db.commit()
    
    return {"message": "Trip cancelled"}


# =============================================================================
# ALERTS ROUTER
# =============================================================================

alerts_router = APIRouter(prefix="/alerts", tags=["Alerts"])


@alerts_router.get("")
async def get_alerts(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    school_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    student_id: Optional[int] = None,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all alerts."""
    query_school_id = school_id or current_user.school_id
    if not query_school_id:
        raise HTTPException(status_code=400, detail="School ID required")
    
    query = db.query(Alert).filter(Alert.school_id == query_school_id)
    
    if vehicle_id:
        query = query.filter(Alert.vehicle_id == vehicle_id)
    if driver_id:
        query = query.filter(Alert.driver_id == driver_id)
    if student_id:
        query = query.filter(Alert.student_id == student_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    total = query.count()
    alerts = query.order_by(desc(Alert.created_at)).offset((page - 1) * limit).limit(limit).all()
    return {"items": alerts, "total": total, "page": page, "limit": limit}


@alerts_router.get("/{alert_id}")
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get alert by ID."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@alerts_router.post("", status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new alert."""
    alert = Alert(**alert_data.dict())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@alerts_router.put("/{alert_id}")
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    for key, value in alert_data.dict(exclude_unset=True).items():
        setattr(alert, key, value)
    
    if alert_data.is_resolved and not alert.resolved_at:
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = current_user.user_id
    
    db.commit()
    db.refresh(alert)
    return alert


@alerts_router.post("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Mark alert as read."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    alert.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert marked as read"}


@alerts_router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Resolve alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.user_id
    if resolution_notes:
        alert.resolution_notes = resolution_notes
    db.commit()
    
    return {"message": "Alert resolved"}


@alerts_router.get("/stats/summary")
async def get_alerts_summary(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    school_id: Optional[int] = None
):
    """Get alerts summary."""
    query_school_id = school_id or current_user.school_id
    
    total = db.query(Alert).filter(Alert.school_id == query_school_id).count()
    unread = db.query(Alert).filter(
        Alert.school_id == query_school_id,
        Alert.is_read == False
    ).count()
    unresolved = db.query(Alert).filter(
        Alert.school_id == query_school_id,
        Alert.is_resolved == False
    ).count()
    
    critical = db.query(Alert).filter(
        Alert.school_id == query_school_id,
        Alert.severity == "critical",
        Alert.is_resolved == False
    ).count()
    
    return {
        "total": total,
        "unread": unread,
        "unresolved": unresolved,
        "critical": critical
    }


# =============================================================================
# MAINTENANCE ROUTER
# =============================================================================

maintenance_router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@maintenance_router.get("")
async def get_maintenance_records(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    vehicle_id: Optional[int] = None,
    maintenance_type: Optional[str] = None,
    upcoming: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get maintenance records."""
    query = db.query(MaintenanceRecord)
    
    if vehicle_id:
        query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
    if maintenance_type:
        query = query.filter(MaintenanceRecord.maintenance_type == maintenance_type)
    if upcoming:
        query = query.filter(MaintenanceRecord.completed_date == None)
    
    total = query.count()
    records = query.order_by(desc(MaintenanceRecord.scheduled_date)).offset((page - 1) * limit).limit(limit).all()
    return {"items": records, "total": total, "page": page, "limit": limit}


@maintenance_router.get("/{record_id}")
async def get_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    """Get maintenance record by ID."""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return record


@maintenance_router.post("", status_code=status.HTTP_201_CREATED)
async def create_maintenance_record(
    record_data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create maintenance record."""
    record = MaintenanceRecord(**record_data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@maintenance_router.put("/{record_id}/complete")
async def complete_maintenance(
    record_id: int,
    cost: Optional[float] = None,
    vendor_name: Optional[str] = None,
    vendor_phone: Optional[str] = None,
    parts_replaced: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Complete maintenance record."""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    record.completed_date = datetime.utcnow()
    if cost is not None:
        record.cost = cost
    if vendor_name:
        record.vendor_name = vendor_name
    if vendor_phone:
        record.vendor_phone = vendor_phone
    if parts_replaced:
        record.parts_replaced = parts_replaced
    
    db.commit()
    
    return {"message": "Maintenance completed", "record": record}


@maintenance_router.get("/upcoming")
async def get_upcoming_maintenance(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365)
):
    """Get upcoming maintenance within specified days."""
    from datetime import timedelta
    future_date = datetime.utcnow() + timedelta(days=days)
    
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.scheduled_date <= future_date,
        MaintenanceRecord.completed_date == None
    ).order_by(MaintenanceRecord.scheduled_date).all()
    
    return {"items": records, "total": len(records)}


@maintenance_router.get("/stats/vehicle/{vehicle_id}")
async def get_vehicle_maintenance_stats(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """Get maintenance stats for a vehicle."""
    total_records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id
    ).count()
    
    completed = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id,
        MaintenanceRecord.completed_date != None
    ).count()
    
    upcoming = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id,
        MaintenanceRecord.completed_date == None
    ).count()
    
    total_cost = db.query(func.sum(MaintenanceRecord.cost)).filter(
        MaintenanceRecord.vehicle_id == vehicle_id,
        MaintenanceRecord.completed_date != None
    ).scalar() or 0
    
    return {
        "total_records": total_records,
        "completed": completed,
        "upcoming": upcoming,
        "total_cost": float(total_cost)
    }


# =============================================================================
# GPS ROUTER
# =============================================================================

gps_router = APIRouter(prefix="/gps", tags=["GPS"])


@gps_router.post("/location")
async def add_gps_location(
    location_data: GPSLocationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Add GPS location."""
    location = GPSLocation(**location_data.dict())
    db.add(location)
    db.commit()
    return {"message": "GPS location recorded"}


@gps_router.get("/latest")
async def get_latest_gps(
    db: Session = Depends(get_db),
    vehicle_id: Optional[int] = None,
    trip_id: Optional[int] = None
):
    """Get latest GPS locations."""
    query = db.query(GPSLocation)
    
    if vehicle_id:
        query = query.filter(GPSLocation.vehicle_id == vehicle_id)
    if trip_id:
        query = query.filter(GPSLocation.trip_id == trip_id)
    
    locations = query.order_by(desc(GPSLocation.created_at)).limit(50).all()
    
    return [
        {
            "id": loc.id,
            "vehicle_id": loc.vehicle_id,
            "trip_id": loc.trip_id,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "altitude": loc.altitude,
            "speed": loc.speed_kmh,
            "direction": loc.direction,
            "accuracy": loc.accuracy,
            "provider": loc.provider,
            "timestamp": loc.created_at
        }
        for loc in locations
    ]


@gps_router.get("/history/{vehicle_id}")
async def get_gps_history(
    vehicle_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get GPS history for a vehicle."""
    query = db.query(GPSLocation).filter(GPSLocation.vehicle_id == vehicle_id)
    
    if start_time:
        query = query.filter(GPSLocation.created_at >= start_time)
    if end_time:
        query = query.filter(GPSLocation.created_at <= end_time)
    
    locations = query.order_by(GPSLocation.created_at).all()
    
    return [
        {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "speed": loc.speed_kmh,
            "timestamp": loc.created_at
        }
        for loc in locations
    ]


# =============================================================================
# ROUTER AGGREGATION
# =============================================================================

all_routes = [
    trips_router,
    alerts_router,
    maintenance_router,
    gps_router
]