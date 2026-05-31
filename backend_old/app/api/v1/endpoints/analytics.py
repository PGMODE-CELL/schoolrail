from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from app.core.security import get_current_user, UserInDB, require_admin

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])


@router.get("/dashboard")
async def get_dashboard_stats(current_user: UserInDB = Depends(get_current_user)):
    from app.services.analytics_service import get_dashboard_stats
    return get_dashboard_stats()


@router.get("/attendance-trend")
async def get_attendance_trend(
    days: int = 30,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.analytics_service import get_monthly_trend
    return {"trend": get_monthly_trend(days)}


@router.get("/vehicle-utilization")
async def get_vehicle_utilization(current_user: UserInDB = Depends(get_current_user)):
    from app.services.analytics_service import get_vehicle_utilization_stats
    return get_vehicle_utilization_stats()


@router.get("/route-performance")
async def get_route_performance(current_user: UserInDB = Depends(get_current_user)):
    from app.services.analytics_service import get_route_performance
    return {"routes": get_route_performance()}


@router.get("/driver-performance")
async def get_driver_performance(current_user: UserInDB = Depends(get_current_user)):
    from app.services.analytics_service import get_driver_performance_summary
    return {"drivers": get_driver_performance_summary()}


@router.get("/fee-collection")
async def get_fee_collection(
    days: int = 30,
    current_user: UserInDB = Depends(require_admin)
):
    from app.services.analytics_service import get_fee_collection_summary
    return get_fee_collection_summary(days)


@router.get("/alerts-summary")
async def get_alerts_summary(current_user: UserInDB = Depends(get_current_user)):
    from app.services.analytics_service import get_alert_summary
    return get_alert_summary()


@router.get("/gps-summary")
async def get_gps_summary(current_user: UserInDB = Depends(get_current_user)):
    from app.services.analytics_service import get_gps_tracking_summary
    return get_gps_tracking_summary()


@router.get("/class-attendance")
async def get_class_attendance(current_user: UserInDB = Depends(get_current_user)):
    from app.services.analytics_service import get_class_wise_attendance
    return {"classes": get_class_wise_attendance()}


@router.get("/revenue")
async def get_revenue_analytics(current_user: UserInDB = Depends(require_admin)):
    from app.services.analytics_service import get_revenue_analytics
    return get_revenue_analytics()


@router.get("/usage-trend")
async def get_usage_trend(
    months: int = 6,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.analytics_service import get_transport_usage_trend
    return {"trend": get_transport_usage_trend(months)}


@router.get("/export")
async def export_analytics(
    report_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "csv",
    current_user: UserInDB = Depends(require_admin)
):
    from app.services.analytics_service import (
        get_dashboard_stats,
        get_route_performance,
        get_driver_performance_summary,
        get_fee_collection_summary
    )
    
    data = {}
    
    if report_type == "dashboard":
        data = get_dashboard_stats()
    elif report_type == "routes":
        data = {"routes": get_route_performance()}
    elif report_type == "drivers":
        data = {"drivers": get_driver_performance_summary()}
    elif report_type == "fees":
        days = 30
        if start_date and end_date:
            from datetime import datetime
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days
        data = get_fee_collection_summary(days)
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    return {
        "report_type": report_type,
        "format": format,
        "data": data,
        "generated_at": datetime.now().isoformat()
    }