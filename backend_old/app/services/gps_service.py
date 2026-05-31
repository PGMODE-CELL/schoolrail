from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.models import GPSLocation, Alert, Vehicle
from app.schemas.schemas import GPSLocationCreate, GPSLocationResponse, AlertResponse


def _gps_location_to_dict(loc: GPSLocation) -> dict:
    return {
        "id": loc.id,
        "vehicle_id": loc.vehicle_id,
        "trip_id": loc.trip_id,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "altitude": loc.altitude,
        "speed_kmh": loc.speed_kmh,
        "direction": loc.direction,
        "created_at": loc.created_at,
    }


def _alert_to_dict(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "uuid": alert.uuid,
        "school_id": alert.school_id,
        "alert_type": alert.alert_type,
        "title": alert.title,
        "message": alert.message,
        "vehicle_id": alert.vehicle_id,
        "driver_id": alert.driver_id,
        "student_id": alert.student_id,
        "route_id": alert.route_id,
        "trip_id": alert.trip_id,
        "severity": alert.severity,
        "latitude": alert.latitude,
        "longitude": alert.longitude,
        "location_name": alert.location_name,
        "is_resolved": alert.is_resolved,
        "resolved_at": alert.resolved_at,
        "is_read": alert.is_read,
        "read_at": alert.read_at,
        "created_at": alert.created_at,
        "updated_at": alert.updated_at,
    }


def record_gps_location(location_data: GPSLocationCreate) -> GPSLocationResponse:
    db = SessionLocal()
    try:
        data = location_data.model_dump()
        location = GPSLocation(**data)
        db.add(location)
        db.commit()
        db.refresh(location)
        return GPSLocationResponse(**_gps_location_to_dict(location))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_vehicle_location(vehicle_id: int) -> Optional[GPSLocationResponse]:
    db = SessionLocal()
    try:
        location = db.query(GPSLocation).filter(
            GPSLocation.vehicle_id == vehicle_id
        ).order_by(GPSLocation.created_at.desc()).first()
        if not location:
            return None
        return GPSLocationResponse(**_gps_location_to_dict(location))
    except Exception:
        return None
    finally:
        db.close()


def get_all_active_vehicles() -> List[GPSLocationResponse]:
    db = SessionLocal()
    try:
        subq = db.query(
            GPSLocation.vehicle_id,
            func.max(GPSLocation.id).label("max_id")
        ).group_by(GPSLocation.vehicle_id).subquery()
        locations = db.query(GPSLocation).join(
            subq, GPSLocation.id == subq.c.max_id
        ).all()
        return [GPSLocationResponse(**_gps_location_to_dict(loc)) for loc in locations]
    except Exception:
        return []
    finally:
        db.close()


def get_vehicle_location_history(vehicle_id: int, hours: int = 24) -> List[GPSLocationResponse]:
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        locations = db.query(GPSLocation).filter(
            GPSLocation.vehicle_id == vehicle_id,
            GPSLocation.created_at >= cutoff
        ).order_by(GPSLocation.created_at.asc()).all()
        return [GPSLocationResponse(**_gps_location_to_dict(loc)) for loc in locations]
    except Exception:
        return []
    finally:
        db.close()


def create_alert(vehicle_id: int, alert_type: str, message: str, severity: str = "info", latitude: float = 0, longitude: float = 0) -> AlertResponse:
    db = SessionLocal()
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        school_id = vehicle.school_id if vehicle else 1
        alert = Alert(
            school_id=school_id,
            vehicle_id=vehicle_id,
            alert_type=alert_type,
            title=alert_type.replace("_", " ").title(),
            message=message,
            severity=severity,
            latitude=latitude,
            longitude=longitude,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return AlertResponse(**_alert_to_dict(alert))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_active_alerts() -> List[AlertResponse]:
    db = SessionLocal()
    try:
        alerts = db.query(Alert).filter(Alert.is_resolved == False).order_by(Alert.created_at.desc()).all()
        return [AlertResponse(**_alert_to_dict(a)) for a in alerts]
    except Exception:
        return []
    finally:
        db.close()


def resolve_alert(alert_id: int, resolved_by: int) -> Optional[AlertResponse]:
    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        db.commit()
        db.refresh(alert)
        return AlertResponse(**_alert_to_dict(alert))
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def get_vehicle_statistics(vehicle_id: int, days: int = 7) -> dict:
    db = SessionLocal()
    try:
        from sqlalchemy import func as sqlfunc
        cutoff = datetime.utcnow() - timedelta(days=days)
        total_records = db.query(sqlfunc.count(GPSLocation.id)).filter(
            GPSLocation.vehicle_id == vehicle_id
        ).scalar() or 0
        max_speed = db.query(sqlfunc.max(GPSLocation.speed_kmh)).filter(
            GPSLocation.vehicle_id == vehicle_id,
            GPSLocation.created_at >= cutoff
        ).scalar() or 0
        latest = db.query(GPSLocation).filter(
            GPSLocation.vehicle_id == vehicle_id
        ).order_by(GPSLocation.created_at.desc()).first()
        return {
            "vehicle_id": vehicle_id,
            "period_days": days,
            "total_records": total_records,
            "max_speed": max_speed,
            "is_active": latest is not None,
        }
    except Exception:
        return {"vehicle_id": vehicle_id, "period_days": days, "total_records": 0, "max_speed": 0, "is_active": False}
    finally:
        db.close()


def geofence_check(vehicle_id: int, route_id: int) -> dict:
    location = get_vehicle_location(vehicle_id)
    if not location:
        return {"in_geofence": False, "message": "No location data"}
    return {
        "in_geofence": True,
        "vehicle_id": vehicle_id,
        "route_id": route_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timestamp": location.created_at,
    }
