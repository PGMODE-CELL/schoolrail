"""
SchoolRail - School Routes
==========================
School management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user, TokenData, require_role
from app.models.models import School, User
from app.schemas.schemas import (
    SchoolCreate, SchoolResponse, SchoolUpdate,
    PaginatedResponse, PaginationParams
)

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.get("", response_model=list[SchoolResponse])
async def get_schools(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get all schools with optional filtering.
    """
    query = db.query(School)
    
    if search:
        query = query.filter(
            (School.name.ilike(f"%{search}%")) |
            (School.code.ilike(f"%{search}%"))
        )
    
    if is_active is not None:
        query = query.filter(School.is_active == is_active)
    
    total = query.count()
    schools = query.offset((page - 1) * limit).limit(limit).all()
    
    return schools


@router.get("/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: int,
    db: Session = Depends(get_db)
):
    """
    Get school by ID.
    """
    school = db.query(School).filter(School.id == school_id).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    return school


@router.post("", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["admin"]))
):
    """
    Create a new school (admin only).
    """
    # Check if school code already exists
    existing = db.query(School).filter(School.code == school_data.code).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School code already exists"
        )
    
    # Create school
    school = School(**school_data.dict())
    db.add(school)
    db.commit()
    db.refresh(school)
    
    return school


@router.put("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    school_data: SchoolUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["admin", "school_admin"]))
):
    """
    Update school (admin or school admin).
    """
    # For school admin, check ownership
    if current_user.role == "school_admin" and current_user.school_id != school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this school"
        )
    
    school = db.query(School).filter(School.id == school_id).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Update fields
    for key, value in school_data.dict(exclude_unset=True).items():
        setattr(school, key, value)
    
    db.commit()
    db.refresh(school)
    
    return school


@router.delete("/{school_id}")
async def delete_school(
    school_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["admin"]))
):
    """
    Delete school (soft delete - admin only).
    """
    school = db.query(School).filter(School.id == school_id).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Soft delete
    school.is_active = False
    db.commit()
    
    return {"message": "School deactivated successfully"}


@router.get("/{school_id}/stats")
async def get_school_stats(
    school_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get school statistics.
    """
    # Check authorization
    if current_user.role != "admin" and current_user.school_id != school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    school = db.query(School).filter(School.id == school_id).first()
    
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    # Get counts
    from app.models.models import Vehicle, Driver, Route, Student, Fee, Trip, Alert
    
    stats = {
        "vehicles": {
            "total": school.vehicles.count(),
            "active": school.vehicles.filter(Vehicle.status == "active").count()
        },
        "drivers": {
            "total": school.drivers.count(),
            "active": school.drivers.filter(Driver.status == "active").count()
        },
        "routes": {
            "total": school.routes.count(),
            "active": school.routes.filter(Route.status == "active").count()
        },
        "students": {
            "total": school.students.count(),
            "active": school.students.filter(Student.status == "active").count()
        },
        "trips": {
            "total": school.trips.count(),
            "today": school.trips.filter(
                func.date(Trip.scheduled_start_time) == func.date(datetime.now())
            ).count()
        },
        "alerts": {
            "unread": school.alerts.filter(Alert.is_read == False).count()
        }
    }
    
    return stats


from datetime import datetime
from sqlalchemy import func