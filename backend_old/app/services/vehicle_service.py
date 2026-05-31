from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Vehicle, MaintenanceRecord
from app.schemas.schemas import VehicleCreate, VehicleResponse, VehicleUpdate


def _vehicle_to_dict(vehicle: Vehicle) -> dict:
    return {
        "id": vehicle.id,
        "uuid": vehicle.uuid,
        "school_id": vehicle.school_id,
        "reg_number": vehicle.reg_number,
        "reg_state": vehicle.reg_state,
        "vehicle_type": vehicle.vehicle_type,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "color": vehicle.color,
        "chassis_number": vehicle.chassis_number,
        "engine_number": vehicle.engine_number,
        "seating_capacity": vehicle.seating_capacity,
        "standing_capacity": vehicle.standing_capacity,
        "total_capacity": vehicle.total_capacity or (vehicle.seating_capacity + (vehicle.standing_capacity or 0)),
        "insurance_expiry": vehicle.insurance_expiry,
        "permit_expiry": vehicle.permit_expiry,
        "fitness_expiry": vehicle.fitness_expiry,
        "gps_device_id": vehicle.gps_device_id,
        "gps_installed": vehicle.gps_installed,
        "status": vehicle.status,
        "is_available": vehicle.is_available,
        "total_km": vehicle.total_km,
        "front_image": vehicle.front_image,
        "created_at": vehicle.created_at,
        "updated_at": vehicle.updated_at,
    }


def get_all_vehicles(status: Optional[str] = None, vehicle_type: Optional[str] = None) -> List[VehicleResponse]:
    db = SessionLocal()
    try:
        query = db.query(Vehicle)
        if status:
            query = query.filter(Vehicle.status == status)
        if vehicle_type:
            query = query.filter(Vehicle.vehicle_type == vehicle_type)
        vehicles = query.all()
        return [VehicleResponse(**_vehicle_to_dict(v)) for v in vehicles]
    except Exception:
        return []
    finally:
        db.close()


def get_vehicle_by_id(vehicle_id: int) -> Optional[VehicleResponse]:
    db = SessionLocal()
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return None
        return VehicleResponse(**_vehicle_to_dict(vehicle))
    except Exception:
        return None
    finally:
        db.close()


def create_vehicle(vehicle_data: VehicleCreate) -> VehicleResponse:
    db = SessionLocal()
    try:
        data = vehicle_data.model_dump()
        vehicle = Vehicle(**data)
        if not vehicle.total_capacity:
            vehicle.total_capacity = vehicle.seating_capacity + (vehicle.standing_capacity or 0)
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
        return VehicleResponse(**_vehicle_to_dict(vehicle))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_vehicle(vehicle_id: int, vehicle_data: VehicleUpdate) -> Optional[VehicleResponse]:
    db = SessionLocal()
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return None
        update_data = vehicle_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vehicle, key, value)
        vehicle.total_capacity = vehicle.seating_capacity + (vehicle.standing_capacity or 0)
        vehicle.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vehicle)
        return VehicleResponse(**_vehicle_to_dict(vehicle))
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def delete_vehicle(vehicle_id: int) -> bool:
    db = SessionLocal()
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return False
        db.delete(vehicle)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def get_vehicle_maintenance_history(vehicle_id: int) -> List[dict]:
    db = SessionLocal()
    try:
        records = db.query(MaintenanceRecord).filter(
            MaintenanceRecord.vehicle_id == vehicle_id
        ).order_by(MaintenanceRecord.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "date": r.completed_date.isoformat() if r.completed_date else (r.scheduled_date.isoformat() if r.scheduled_date else None),
                "type": r.maintenance_type,
                "description": r.title,
                "cost": r.cost,
            }
            for r in records
        ]
    except Exception:
        return []
    finally:
        db.close()


def get_vehicle_utilization(vehicle_id: int, days: int = 30) -> dict:
    db = SessionLocal()
    try:
        from app.models.models import Trip
        from sqlalchemy import func
        cutoff = datetime.utcnow() - timedelta(days=days)
        trip_count = db.query(func.count(Trip.id)).filter(
            Trip.vehicle_id == vehicle_id,
            Trip.created_at >= cutoff,
            Trip.status == "completed"
        ).scalar() or 0
        total_distance = db.query(func.sum(Trip.distance_km)).filter(
            Trip.vehicle_id == vehicle_id,
            Trip.created_at >= cutoff
        ).scalar() or 0
        return {
            "vehicle_id": vehicle_id,
            "period_days": days,
            "total_trips": trip_count,
            "total_distance": round(total_distance, 2),
            "average_occupancy": 0,
            "utilization_rate": 0.0,
            "downtime_days": 0,
        }
    except Exception:
        return {"vehicle_id": vehicle_id, "period_days": days, "total_trips": 0, "total_distance": 0}
    finally:
        db.close()


def schedule_maintenance(vehicle_id: int, maintenance_date: str, description: str) -> dict:
    db = SessionLocal()
    try:
        record = MaintenanceRecord(
            vehicle_id=vehicle_id,
            maintenance_type="scheduled",
            title=description,
            description=description,
            scheduled_date=datetime.fromisoformat(maintenance_date),
        )
        db.add(record)
        db.commit()
        return {
            "message": "Maintenance scheduled",
            "vehicle_id": vehicle_id,
            "scheduled_date": maintenance_date,
            "description": description,
        }
    except Exception:
        db.rollback()
        return {"message": "Failed to schedule maintenance", "vehicle_id": vehicle_id}
    finally:
        db.close()
