from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.core.security import get_current_user, require_admin
from app.services.gps_service import (
    record_gps_location,
    get_vehicle_location,
    get_all_active_vehicles,
    get_vehicle_location_history,
    get_active_alerts,
    resolve_alert,
    get_vehicle_statistics,
    geofence_check,
)
from app.schemas.schemas import GPSLocationCreate, GPSLocationResponse, AlertResponse, AlertResolve

router = APIRouter(prefix="/gps", tags=["GPS Tracking"])


@router.post("/location", response_model=GPSLocationResponse)
async def record_location(
    location_data: GPSLocationCreate,
    current_user=Depends(get_current_user)
):
    return record_gps_location(location_data)


@router.get("/vehicle/{vehicle_id}", response_model=GPSLocationResponse)
async def get_current_location(
    vehicle_id: int,
    current_user=Depends(get_current_user)
):
    location = get_vehicle_location(vehicle_id)
    if not location:
        raise HTTPException(status_code=404, detail="No location data for this vehicle")
    return location


@router.get("/active", response_model=List[GPSLocationResponse])
async def get_all_active_locations(
    current_user=Depends(get_current_user)
):
    return get_all_active_vehicles()


@router.get("/vehicle/{vehicle_id}/history", response_model=List[GPSLocationResponse])
async def get_history(
    vehicle_id: int,
    hours: int = Query(24),
    current_user=Depends(get_current_user)
):
    return get_vehicle_location_history(vehicle_id, hours)


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(current_user=Depends(get_current_user)):
    return get_active_alerts()


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert_by_id(
    alert_id: int,
    resolve_data: AlertResolve,
    current_user=Depends(require_admin)
):
    alert = resolve_alert(alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.get("/vehicle/{vehicle_id}/statistics")
async def get_vehicle_stats(
    vehicle_id: int,
    days: int = Query(7),
    current_user=Depends(get_current_user)
):
    return get_vehicle_statistics(vehicle_id, days)


@router.get("/vehicle/{vehicle_id}/geofence/{route_id}")
async def check_geofence(
    vehicle_id: int,
    route_id: int,
    current_user=Depends(get_current_user)
):
    return geofence_check(vehicle_id, route_id)
