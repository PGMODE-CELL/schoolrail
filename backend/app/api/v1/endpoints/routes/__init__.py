from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_current_user, require_admin
from app.services.route_service import (
    get_all_routes,
    get_route_by_id,
    create_route,
    update_route,
    delete_route,
    get_route_stops,
    add_stop_to_route,
    optimize_route,
)
from app.schemas.route import (
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    RouteWithStops,
    StopCreate,
    StopResponse,
)

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("/", response_model=List[RouteWithStops])
async def list_routes(current_user=Depends(get_current_user)):
    return get_all_routes()


@router.get("/{route_id}", response_model=RouteWithStops)
async def get_route(route_id: int, current_user=Depends(get_current_user)):
    route = get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.post("/", response_model=RouteWithStops)
async def create_new_route(route_data: RouteCreate, current_user=Depends(require_admin)):
    return create_route(route_data)


@router.put("/{route_id}", response_model=RouteWithStops)
async def update_existing_route(route_id: int, route_data: RouteUpdate, current_user=Depends(require_admin)):
    route = update_route(route_id, route_data)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete("/{route_id}")
async def delete_existing_route(route_id: int, current_user=Depends(require_admin)):
    if not delete_route(route_id):
        raise HTTPException(status_code=404, detail="Route not found")
    return {"message": "Route deleted successfully"}


@router.get("/{route_id}/stops", response_model=List[StopResponse])
async def list_route_stops(route_id: int, current_user=Depends(get_current_user)):
    route = get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return get_route_stops(route_id)


@router.post("/{route_id}/stops", response_model=StopResponse)
async def add_stop(route_id: int, stop_data: StopCreate, current_user=Depends(require_admin)):
    stop = add_stop_to_route(route_id, stop_data)
    if not stop:
        raise HTTPException(status_code=404, detail="Route not found")
    return stop


@router.post("/{route_id}/optimize")
async def optimize_existing_route(route_id: int, current_user=Depends(require_admin)):
    result = optimize_route(route_id)
    if not result:
        raise HTTPException(status_code=404, detail="Route not found")
    return result
