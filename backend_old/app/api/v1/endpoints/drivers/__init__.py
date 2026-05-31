from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.core.security import get_current_user, require_admin, require_driver_or_admin
from app.services.driver_service import (
    get_all_drivers,
    get_driver_by_id,
    create_driver,
    update_driver,
    delete_driver,
    assign_driver_to_vehicle,
    get_driver_trips,
    get_driver_performance,
)
from app.schemas.schemas import DriverCreate, DriverResponse, DriverUpdate

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("/", response_model=List[DriverResponse])
async def list_drivers(
    status: Optional[str] = Query(None),
    vehicle_id: Optional[int] = Query(None),
    current_user=Depends(get_current_user)
):
    return get_all_drivers(status, vehicle_id)


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(driver_id: int, current_user=Depends(get_current_user)):
    driver = get_driver_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.post("/", response_model=DriverResponse)
async def create_new_driver(
    driver_data: DriverCreate,
    current_user=Depends(require_admin)
):
    return create_driver(driver_data)


@router.put("/{driver_id}", response_model=DriverResponse)
async def update_existing_driver(
    driver_id: int,
    driver_data: DriverUpdate,
    current_user=Depends(require_admin)
):
    driver = update_driver(driver_id, driver_data)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.delete("/{driver_id}")
async def delete_existing_driver(
    driver_id: int,
    current_user=Depends(require_admin)
):
    if not delete_driver(driver_id):
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": "Driver deleted successfully"}


@router.post("/{driver_id}/assign-vehicle")
async def assign_vehicle(
    driver_id: int,
    vehicle_id: int,
    current_user=Depends(require_admin)
):
    result = assign_driver_to_vehicle(driver_id, vehicle_id)
    if not result:
        raise HTTPException(status_code=400, detail="Could not assign vehicle")
    return result


@router.get("/{driver_id}/trips")
async def get_driver_trip_history(
    driver_id: int,
    current_user=Depends(get_current_user)
):
    return get_driver_trips(driver_id)


@router.get("/{driver_id}/performance")
async def get_driver_performance_stats(
    driver_id: int,
    current_user=Depends(get_current_user)
):
    return get_driver_performance(driver_id)
