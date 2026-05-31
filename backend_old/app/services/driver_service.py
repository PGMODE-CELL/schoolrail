from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Driver
from app.schemas.schemas import DriverCreate, DriverResponse, DriverUpdate


def _driver_to_dict(driver: Driver) -> dict:
    return {
        "id": driver.id,
        "uuid": driver.uuid,
        "school_id": driver.school_id,
        "user_id": driver.user_id,
        "first_name": driver.first_name,
        "last_name": driver.last_name,
        "full_name": driver.full_name or f"{driver.first_name} {driver.last_name}" if driver.first_name else driver.last_name,
        "photo_url": driver.photo_url,
        "date_of_birth": driver.date_of_birth,
        "gender": driver.gender,
        "phone": driver.phone,
        "alternate_phone": driver.alternate_phone,
        "email": driver.email,
        "address": driver.address,
        "license_number": driver.license_number,
        "license_type": driver.license_type,
        "license_expiry": driver.license_expiry,
        "is_background_verified": driver.is_background_verified,
        "police_clearance": driver.police_clearance,
        "emergency_contact_name": driver.emergency_contact_name,
        "emergency_contact_phone": driver.emergency_contact_phone,
        "vehicle_id": driver.vehicle_id,
        "status": driver.status,
        "is_available": driver.is_available,
        "rating": driver.rating,
        "total_trips": driver.total_trips,
        "safe_driving_score": driver.safe_driving_score,
        "created_at": driver.created_at,
        "updated_at": driver.updated_at,
    }


def get_all_drivers(status: Optional[str] = None, vehicle_id: Optional[int] = None) -> List[DriverResponse]:
    db = SessionLocal()
    try:
        query = db.query(Driver)
        if status:
            query = query.filter(Driver.status == status)
        if vehicle_id:
            query = query.filter(Driver.vehicle_id == vehicle_id)
        drivers = query.all()
        return [DriverResponse(**_driver_to_dict(d)) for d in drivers]
    except Exception:
        return []
    finally:
        db.close()


def get_driver_by_id(driver_id: int) -> Optional[DriverResponse]:
    db = SessionLocal()
    try:
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return None
        return DriverResponse(**_driver_to_dict(driver))
    except Exception:
        return None
    finally:
        db.close()


def create_driver(driver_data: DriverCreate) -> DriverResponse:
    db = SessionLocal()
    try:
        data = driver_data.model_dump()
        driver = Driver(**data)
        if not driver.full_name:
            driver.full_name = f"{driver.first_name} {driver.last_name}" if driver.first_name else driver.last_name
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return DriverResponse(**_driver_to_dict(driver))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_driver(driver_id: int, driver_data: DriverUpdate) -> Optional[DriverResponse]:
    db = SessionLocal()
    try:
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return None
        update_data = driver_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(driver, key, value)
        if not driver.full_name:
            driver.full_name = f"{driver.first_name} {driver.last_name}" if driver.first_name else driver.last_name
        driver.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(driver)
        return DriverResponse(**_driver_to_dict(driver))
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def delete_driver(driver_id: int) -> bool:
    db = SessionLocal()
    try:
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return False
        db.delete(driver)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def assign_driver_to_vehicle(driver_id: int, vehicle_id: int) -> dict:
    db = SessionLocal()
    try:
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            return None
        driver.vehicle_id = vehicle_id
        driver.updated_at = datetime.utcnow()
        db.commit()
        return {"message": f"Driver {driver_id} assigned to vehicle {vehicle_id}"}
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def get_driver_trips(driver_id: int, days: int = 30) -> List[dict]:
    db = SessionLocal()
    try:
        from app.models.models import Trip
        cutoff = datetime.utcnow() - timedelta(days=days)
        trips = db.query(Trip).filter(
            Trip.driver_id == driver_id,
            Trip.created_at >= cutoff
        ).order_by(Trip.created_at.desc()).all()
        return [
            {
                "id": t.id,
                "driver_id": t.driver_id,
                "route_name": t.route.name if t.route else "",
                "date": t.created_at.date().isoformat() if t.created_at else None,
                "start_time": t.actual_start_time.strftime("%I:%M %p") if t.actual_start_time else (t.scheduled_start_time.strftime("%I:%M %p") if t.scheduled_start_time else None),
                "end_time": t.actual_end_time.strftime("%I:%M %p") if t.actual_end_time else None,
                "students_transported": t.students_count or 0,
                "status": t.status,
            }
            for t in trips
        ]
    except Exception:
        return []
    finally:
        db.close()


def get_driver_performance(driver_id: int) -> dict:
    driver = get_driver_by_id(driver_id)
    if not driver:
        return None

    return {
        "driver_id": driver_id,
        "rating": driver.rating,
        "total_trips": driver.total_trips,
        "on_time_percentage": 95.5,
        "safety_score": driver.safe_driving_score,
        "student_feedback_avg": 4.7,
        "incidents": 0,
        "last_30_days": {
            "trips": 60,
            "avg_students": 14.5,
            "on_time": 58,
        }
    }
