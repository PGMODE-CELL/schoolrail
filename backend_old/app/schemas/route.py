from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RouteBase(BaseModel):
    name: str
    description: Optional[str] = None


class RouteCreate(RouteBase):
    school_id: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    total_distance: Optional[float] = None
    estimated_time: Optional[int] = None
    start_location: Optional[str] = None
    end_location: Optional[str] = None


class RouteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    total_distance: Optional[float] = None
    estimated_time: Optional[int] = None
    status: Optional[str] = None


class RouteResponse(RouteBase):
    id: int
    school_id: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    total_distance: Optional[float] = None
    estimated_time: Optional[int] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StopBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    sequence_order: int
    arrival_time: Optional[str] = None


class StopCreate(StopBase):
    route_id: int


class StopUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    sequence_order: Optional[int] = None
    arrival_time: Optional[str] = None


class StopResponse(StopBase):
    id: int
    route_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RouteWithStops(RouteResponse):
    stops: List[StopResponse] = []
