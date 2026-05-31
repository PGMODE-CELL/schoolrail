from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.core.security import get_current_user, require_admin
from app.services.vehicle_service import (
    get_all_vehicles,
    get_vehicle_by_id,
    create_vehicle,
    update_vehicle,
    delete_vehicle,
    get_vehicle_maintenance_history,
    get_vehicle_utilization,
    schedule_maintenance,
)
from app.schemas.schemas import VehicleCreate, VehicleResponse, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/", response_model=List[VehicleResponse])
async def list_vehicles(
    status: Optional[str] = Query(None),
    vehicle_type: Optional[str] = Query(None),
    current_user=Depends(get_current_user)
):
    return get_all_vehicles(status, vehicle_type)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: int, current_user=Depends(get_current_user)):
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.post("/", response_model=VehicleResponse)
async def create_new_vehicle(
    vehicle_data: VehicleCreate,
    current_user=Depends(require_admin)
):
    return create_vehicle(vehicle_data)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_existing_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user=Depends(require_admin)
):
    vehicle = update_vehicle(vehicle_id, vehicle_data)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.delete("/{vehicle_id}")
async def delete_existing_vehicle(
    vehicle_id: int,
    current_user=Depends(require_admin)
):
    if not delete_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}


@router.get("/{vehicle_id}/maintenance")
async def get_maintenance_history(
    vehicle_id: int,
    current_user=Depends(get_current_user)
):
    return get_vehicle_maintenance_history(vehicle_id)


@router.get("/{vehicle_id}/utilization")
async def get_utilization_stats(
    vehicle_id: int,
    days: int = Query(30),
    current_user=Depends(get_current_user)
):
    return get_vehicle_utilization(vehicle_id, days)


@router.post("/{vehicle_id}/schedule-maintenance")
async def schedule_vehicle_maintenance(
    vehicle_id: int,
    maintenance_date: str,
    description: str,
    current_user=Depends(require_admin)
):
    return schedule_maintenance(vehicle_id, maintenance_date, description)
