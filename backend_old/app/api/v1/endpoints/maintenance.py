"""
SchoolRail - Maintenance and Vehicle Management API
====================================================
Complete API for vehicle maintenance, service records,
parts inventory, and maintenance scheduling.

Author: SchoolRail Team
License: MIT
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel

from ....core.database import get_db
from ....core.security import get_current_user, UserInDB
from ....models.models import Vehicle, MaintenanceRecord, Driver, User
from ....utils.helpers import ResponseHelper

router = APIRouter()


class MaintenanceRecordCreate(BaseModel):
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


class MaintenanceRecordUpdate(BaseModel):
    completed_date: Optional[datetime] = None
    odometer_reading: Optional[float] = None
    cost: Optional[float] = None
    vendor_name: Optional[str] = None
    vendor_phone: Optional[str] = None
    parts_replaced: Optional[str] = None
    notes: Optional[str] = None
    next_due_date: Optional[datetime] = None
    next_due_km: Optional[float] = None


class MaintenanceScheduleCreate(BaseModel):
    vehicle_id: int
    maintenance_type: str
    title: str
    interval_km: int
    interval_days: int
    description: Optional[str] = None


@router.get("/maintenance/records")
async def get_maintenance_records(
    vehicle_id: Optional[int] = None,
    maintenance_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get maintenance records"""
    query = db.query(MaintenanceRecord)
    
    if vehicle_id:
        query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
    
    if maintenance_type:
        query = query.filter(MaintenanceRecord.maintenance_type == maintenance_type)
    
    if status == "pending":
        query = query.filter(MaintenanceRecord.completed_date == None)
    elif status == "completed":
        query = query.filter(MaintenanceRecord.completed_date != None)
    
    if start_date:
        query = query.filter(MaintenanceRecord.scheduled_date >= datetime.fromisoformat(start_date))
    
    if end_date:
        query = query.filter(MaintenanceRecord.scheduled_date <= datetime.fromisoformat(end_date))
    
    total = query.count()
    offset = (page - 1) * limit
    records = query.order_by(MaintenanceRecord.scheduled_date.desc()).offset(offset).limit(limit).all()
    
    items = []
    for record in records:
        vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
        items.append({
            "id": record.id,
            "vehicle_id": record.vehicle_id,
            "vehicle_number": vehicle.reg_number if vehicle else None,
            "maintenance_type": record.maintenance_type,
            "title": record.title,
            "description": record.description,
            "scheduled_date": record.scheduled_date.isoformat() if record.scheduled_date else None,
            "completed_date": record.completed_date.isoformat() if record.completed_date else None,
            "odometer_reading": record.odometer_reading,
            "cost": record.cost,
            "vendor_name": record.vendor_name,
            "vendor_phone": record.vendor_phone,
            "parts_replaced": record.parts_replaced,
            "next_due_date": record.next_due_date.isoformat() if record.next_due_date else None,
            "next_due_km": record.next_due_km,
            "is_completed": record.completed_date != None
        })
    
    return ResponseHelper.success(ResponseHelper.paginate(items, page, limit, total))


@router.post("/maintenance/records")
async def create_maintenance_record(
    record: MaintenanceRecordCreate,
    db: Session = Depends(get_db)
):
    """Create new maintenance record"""
    maintenance = MaintenanceRecord(
        vehicle_id=record.vehicle_id,
        maintenance_type=record.maintenance_type,
        title=record.title,
        description=record.description,
        scheduled_date=record.scheduled_date or datetime.now(),
        odometer_reading=record.odometer_reading,
        cost=record.cost,
        vendor_name=record.vendor_name,
        vendor_phone=record.vendor_phone,
        parts_replaced=record.parts_replaced,
        next_due_date=record.next_due_date,
        next_due_km=record.next_due_km
    )
    
    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)
    
    return ResponseHelper.success({"id": maintenance.id}, "Maintenance record created")


@router.get("/maintenance/records/{record_id}")
async def get_maintenance_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """Get single maintenance record"""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
    
    return ResponseHelper.success({
        "id": record.id,
        "vehicle_id": record.vehicle_id,
        "vehicle_number": vehicle.reg_number if vehicle else None,
        "maintenance_type": record.maintenance_type,
        "title": record.title,
        "description": record.description,
        "scheduled_date": record.scheduled_date.isoformat() if record.scheduled_date else None,
        "completed_date": record.completed_date.isoformat() if record.completed_date else None,
        "odometer_reading": record.odometer_reading,
        "cost": record.cost,
        "vendor_name": record.vendor_name,
        "vendor_phone": record.vendor_phone,
        "parts_replaced": record.parts_replaced,
        "next_due_date": record.next_due_date.isoformat() if record.next_due_date else None,
        "next_due_km": record.next_due_km,
        "is_completed": record.completed_date != None
    })


@router.put("/maintenance/records/{record_id}")
async def update_maintenance_record(
    record_id: int,
    record_update: MaintenanceRecordUpdate,
    db: Session = Depends(get_db)
):
    """Update maintenance record"""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    if record_update.completed_date:
        record.completed_date = record_update.completed_date
    if record_update.odometer_reading:
        record.odometer_reading = record_update.odometer_reading
    if record_update.cost:
        record.cost = record_update.cost
    if record_update.vendor_name:
        record.vendor_name = record_update.vendor_name
    if record_update.vendor_phone:
        record.vendor_phone = record_update.vendor_phone
    if record_update.parts_replaced:
        record.parts_replaced = record_update.parts_replaced
    if record_update.notes:
        record.description = record_update.notes
    if record_update.next_due_date:
        record.next_due_date = record_update.next_due_date
    if record_update.next_due_km:
        record.next_due_km = record_update.next_due_km
    
    db.commit()
    
    return ResponseHelper.success({"id": record.id}, "Maintenance record updated")


@router.delete("/maintenance/records/{record_id}")
async def delete_maintenance_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """Delete maintenance record"""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    db.delete(record)
    db.commit()
    
    return ResponseHelper.success(None, "Maintenance record deleted")


@router.get("/maintenance/schedule")
async def get_maintenance_schedule(
    vehicle_id: Optional[int] = None,
    upcoming_days: int = Query(30),
    db: Session = Depends(get_db)
):
    """Get upcoming maintenance schedule"""
    end_date = datetime.now() + timedelta(days=upcoming_days)
    
    query = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.completed_date == None,
        MaintenanceRecord.scheduled_date <= end_date
    )
    
    if vehicle_id:
        query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
    
    records = query.order_by(MaintenanceRecord.scheduled_date.asc()).all()
    
    items = []
    for record in records:
        vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
        items.append({
            "id": record.id,
            "vehicle_id": record.vehicle_id,
            "vehicle_number": vehicle.reg_number if vehicle else None,
            "maintenance_type": record.maintenance_type,
            "title": record.title,
            "scheduled_date": record.scheduled_date.isoformat() if record.scheduled_date else None,
            "days_until": (record.scheduled_date - datetime.now()).days if record.scheduled_date else None
        })
    
    return ResponseHelper.success(items)


@router.get("/maintenance/overdue")
async def get_overdue_maintenance(
    db: Session = Depends(get_db)
):
    """Get overdue maintenance items"""
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.completed_date == None,
        MaintenanceRecord.scheduled_date < datetime.now()
    ).all()
    
    items = []
    for record in records:
        vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
        days_overdue = (datetime.now() - record.scheduled_date).days if record.scheduled_date else 0
        items.append({
            "id": record.id,
            "vehicle_id": record.vehicle_id,
            "vehicle_number": vehicle.reg_number if vehicle else None,
            "maintenance_type": record.maintenance_type,
            "title": record.title,
            "scheduled_date": record.scheduled_date.isoformat() if record.scheduled_date else None,
            "days_overdue": days_overdue
        })
    
    return ResponseHelper.success(items)


@router.get("/maintenance/stats")
async def get_maintenance_stats(
    vehicle_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get maintenance statistics"""
    query = db.query(MaintenanceRecord)
    
    if vehicle_id:
        query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
    
    total_records = query.count()
    completed = query.filter(MaintenanceRecord.completed_date != None).count()
    pending = total_records - completed
    
    total_cost = query.filter(MaintenanceRecord.completed_date != None).with_entities(
        db.query(db.func.sum(MaintenanceRecord.cost)).scalar()
    ).scalar() or 0
    
    avg_cost = (total_cost / completed) if completed > 0 else 0
    
    upcoming = query.filter(
        MaintenanceRecord.completed_date == None,
        MaintenanceRecord.scheduled_date >= datetime.now(),
        MaintenanceRecord.scheduled_date <= datetime.now() + timedelta(days=7)
    ).count()
    
    overdue = query.filter(
        MaintenanceRecord.completed_date == None,
        MaintenanceRecord.scheduled_date < datetime.now()
    ).count()
    
    type_breakdown = {}
    types = query.with_entities(MaintenanceRecord.maintenance_type).distinct().all()
    for t in types:
        count = query.filter(MaintenanceRecord.maintenance_type == t[0]).count()
        type_breakdown[t[0]] = count
    
    return ResponseHelper.success({
        "total_records": total_records,
        "completed": completed,
        "pending": pending,
        "total_cost": total_cost,
        "average_cost": avg_cost,
        "upcoming": upcoming,
        "overdue": overdue,
        "type_breakdown": type_breakdown
    })


@router.post("/maintenance/complete/{record_id}")
async def complete_maintenance(
    record_id: int,
    odometer_reading: float = None,
    cost: float = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Mark maintenance as completed"""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    record.completed_date = datetime.now()
    if odometer_reading:
        record.odometer_reading = odometer_reading
    if cost:
        record.cost = cost
    if notes:
        record.description = notes
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
    if vehicle and odometer_reading:
        vehicle.total_km = odometer_reading
    
    if record.next_service_date:
        new_record = MaintenanceRecord(
            vehicle_id=record.vehicle_id,
            maintenance_type=record.maintenance_type,
            title=f"Next {record.title}",
            scheduled_date=record.next_due_date,
            next_due_km=record.next_due_km
        )
        db.add(new_record)
    
    db.commit()
    
    return ResponseHelper.success({"id": record.id}, "Maintenance completed")


@router.get("/maintenance/types")
async def get_maintenance_types():
    """Get list of maintenance types"""
    return ResponseHelper.success([
        {"id": "oil_change", "name": "Oil Change", "icon": "water"},
        {"id": "tire_rotation", "name": "Tire Rotation", "icon": "sync"},
        {"id": "brake_service", "name": "Brake Service", "icon": "warning"},
        {"id": "battery", "name": "Battery", "icon": "battery-full"},
        {"id": "engine", "name": "Engine Service", "icon": "cog"},
        {"id": "transmission", "name": "Transmission", "icon": "sync"},
        {"id": "ac", "name": "AC Service", "icon": "snow"},
        {"id": "electrical", "name": "Electrical", "icon": "flash"},
        {"id": "body", "name": "Body Work", "icon": "car"},
        {"id": "inspection", "name": "Inspection", "icon": "search"},
    ])


@router.get("/vehicles/{vehicle_id}/maintenance/history")
async def get_vehicle_maintenance_history(
    vehicle_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get maintenance history for specific vehicle"""
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id
    ).order_by(MaintenanceRecord.completed_date.desc() if MaintenanceRecord.completed_date else MaintenanceRecord.scheduled_date.desc()).limit(limit).all()
    
    items = []
    for record in records:
        items.append({
            "id": record.id,
            "maintenance_type": record.maintenance_type,
            "title": record.title,
            "completed_date": record.completed_date.isoformat() if record.completed_date else None,
            "odometer_reading": record.odometer_reading,
            "cost": record.cost,
            "is_completed": record.completed_date != None
        })
    
    return ResponseHelper.success(items)


@router.get("/vehicles/{vehicle_id}/maintenance/upcoming")
async def get_vehicle_upcoming_maintenance(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """Get upcoming maintenance for vehicle"""
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id,
        MaintenanceRecord.completed_date == None,
        MaintenanceRecord.scheduled_date >= datetime.now()
    ).order_by(MaintenanceRecord.scheduled_date.asc()).all()
    
    items = []
    for record in records:
        days_until = (record.scheduled_date - datetime.now()).days if record.scheduled_date else None
        items.append({
            "id": record.id,
            "maintenance_type": record.maintenance_type,
            "title": record.title,
            "scheduled_date": record.scheduled_date.isoformat() if record.scheduled_date else None,
            "days_until": days_until,
            "priority": "overdue" if days_until and days_until < 0 else "normal" if days_until and days_until > 7 else "soon"
        })
    
    return ResponseHelper.success(items)