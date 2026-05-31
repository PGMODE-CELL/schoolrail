"""
SchoolRail - Main API Router
============================
Combines all API endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, schools, vehicles, drivers
from app.api.v1.endpoints import operations
from app.api.v1.endpoints import extras, analytics, maintenance
from app.api.v1.endpoints.routes import router as routes_router
from app.api.v1.endpoints.students import router as students_router
from app.api.v1.endpoints.attendance import router as attendance_router
from app.api.v1.endpoints.remaining import fees_router
from app.api.v1.endpoints.gps import router as gps_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.scan import router as scan_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.parent import router as parent_router
from app.api.v1.endpoints.driver import router as driver_router
from app.api.v1.endpoints.websocket import router as websocket_router

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(schools.router)
api_router.include_router(vehicles.router)
api_router.include_router(drivers.router)

api_router.include_router(routes_router)
api_router.include_router(students_router)
api_router.include_router(attendance_router)
api_router.include_router(fees_router)
api_router.include_router(gps_router)

api_router.include_router(operations.trips_router)
api_router.include_router(operations.alerts_router)
api_router.include_router(operations.maintenance_router)

api_router.include_router(notifications_router)
api_router.include_router(scan_router)
api_router.include_router(reports_router)
api_router.include_router(parent_router)
api_router.include_router(driver_router)
api_router.include_router(websocket_router)

api_router.include_router(extras.router, prefix="/extras", tags=["Extras"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(maintenance.router, prefix="/maintenance-alt", tags=["Maintenance Alt"])