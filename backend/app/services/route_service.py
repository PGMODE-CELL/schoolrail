from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Route, Stop
from app.schemas.route import RouteCreate, RouteUpdate, RouteResponse, RouteWithStops, StopCreate, StopResponse


def _route_to_dict(route: Route) -> dict:
    return {
        "id": route.id,
        "name": route.name,
        "description": route.description,
        "school_id": route.school_id,
        "vehicle_id": route.vehicle_id,
        "driver_id": route.driver_id,
        "total_distance": route.total_distance_km,
        "estimated_time": route.estimated_time_minutes,
        "status": route.status,
        "start_location": route.start_point,
        "end_location": route.end_point,
        "created_at": route.created_at,
        "updated_at": route.updated_at,
    }


def _stop_to_dict(stop: Stop) -> dict:
    return {
        "id": stop.id,
        "name": stop.name,
        "latitude": stop.latitude,
        "longitude": stop.longitude,
        "sequence_order": stop.stop_order,
        "arrival_time": stop.estimated_arrival_time,
        "route_id": stop.route_id,
        "created_at": stop.created_at,
    }


def get_all_routes() -> List[RouteWithStops]:
    db = SessionLocal()
    try:
        routes = db.query(Route).all()
        result = []
        for route in routes:
            stops = db.query(Stop).filter(Stop.route_id == route.id).order_by(Stop.stop_order).all()
            route_dict = _route_to_dict(route)
            route_dict["stops"] = [_stop_to_dict(s) for s in stops]
            result.append(RouteWithStops(**route_dict))
        return result
    except Exception:
        return []
    finally:
        db.close()


def get_route_by_id(route_id: int) -> Optional[RouteWithStops]:
    db = SessionLocal()
    try:
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            return None
        stops = db.query(Stop).filter(Stop.route_id == route.id).order_by(Stop.stop_order).all()
        route_dict = _route_to_dict(route)
        route_dict["stops"] = [_stop_to_dict(s) for s in stops]
        return RouteWithStops(**route_dict)
    except Exception:
        return None
    finally:
        db.close()


def create_route(route_data: RouteCreate) -> RouteWithStops:
    db = SessionLocal()
    try:
        data = route_data.model_dump(exclude={"stops"})
        route = Route(**data)
        db.add(route)
        db.commit()
        db.refresh(route)

        stops_data = getattr(route_data, "stops", None) or []
        for stop_data in stops_data:
            stop_dict = stop_data.model_dump() if hasattr(stop_data, "model_dump") else stop_dict
            stop = Stop(
                route_id=route.id,
                name=stop_dict.get("name"),
                latitude=stop_dict.get("latitude"),
                longitude=stop_dict.get("longitude"),
                stop_order=stop_dict.get("sequence_order"),
                estimated_arrival_time=stop_dict.get("arrival_time"),
            )
            db.add(stop)
        db.commit()

        stops = db.query(Stop).filter(Stop.route_id == route.id).order_by(Stop.stop_order).all()
        route_dict = _route_to_dict(route)
        route_dict["stops"] = [_stop_to_dict(s) for s in stops]
        return RouteWithStops(**route_dict)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_route(route_id: int, route_data: RouteUpdate) -> Optional[RouteWithStops]:
    db = SessionLocal()
    try:
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            return None
        update_data = route_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(route, key, value)
        route.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(route)

        stops = db.query(Stop).filter(Stop.route_id == route.id).order_by(Stop.stop_order).all()
        route_dict = _route_to_dict(route)
        route_dict["stops"] = [_stop_to_dict(s) for s in stops]
        return RouteWithStops(**route_dict)
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def delete_route(route_id: int) -> bool:
    db = SessionLocal()
    try:
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            return False
        db.query(Stop).filter(Stop.route_id == route_id).delete()
        db.delete(route)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def get_route_stops(route_id: int) -> List[StopResponse]:
    db = SessionLocal()
    try:
        stops = db.query(Stop).filter(Stop.route_id == route_id).order_by(Stop.stop_order).all()
        return [StopResponse(**_stop_to_dict(s)) for s in stops]
    except Exception:
        return []
    finally:
        db.close()


def add_stop_to_route(route_id: int, stop_data: StopCreate) -> Optional[StopResponse]:
    db = SessionLocal()
    try:
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            return None
        stop_dict = stop_data.model_dump()
        stop = Stop(
            route_id=route_id,
            name=stop_dict.get("name"),
            latitude=stop_dict.get("latitude"),
            longitude=stop_dict.get("longitude"),
            stop_order=stop_dict.get("sequence_order"),
            estimated_arrival_time=stop_dict.get("arrival_time"),
        )
        db.add(stop)
        db.commit()
        db.refresh(stop)
        return StopResponse(**_stop_to_dict(stop))
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()


def optimize_route(route_id: int) -> Optional[dict]:
    db = SessionLocal()
    try:
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            return None
        stops = db.query(Stop).filter(Stop.route_id == route_id).order_by(Stop.stop_order).all()
        if len(stops) < 2:
            return {"optimized": False, "message": "Not enough stops to optimize"}

        total_distance = 0.0
        for i in range(len(stops) - 1):
            lat1, lon1 = stops[i].latitude, stops[i].longitude
            lat2, lon2 = stops[i + 1].latitude, stops[i + 1].longitude
            total_distance += ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111.0

        return {
            "optimized": True,
            "total_distance": round(total_distance, 2),
            "estimated_time": int(total_distance * 3),
            "stops_count": len(stops)
        }
    except Exception:
        return None
    finally:
        db.close()
