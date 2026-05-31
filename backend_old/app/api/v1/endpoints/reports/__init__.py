from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import date, datetime
from io import BytesIO
from app.core.security import get_current_user, require_admin
from app.services.report_service import (
    report_generator,
    get_available_report_types,
    generate_attendance_report_csv,
    generate_fee_report_csv,
    generate_student_list_csv,
    generate_vehicle_report_csv,
    generate_route_report_csv,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/types")
async def list_report_types(current_user=Depends(get_current_user)):
    return {"reports": get_available_report_types()}


@router.get("/attendance")
async def generate_attendance_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    route_id: Optional[int] = Query(None),
    format: str = Query("csv"),
    current_user=Depends(get_current_user)
):
    from app.services.attendance_service import get_attendance_by_date
    
    all_records = []
    current_date = start_date
    
    while current_date <= end_date:
        records = get_attendance_by_date(current_date)
        for record in records:
            all_records.append({
                "date": current_date.isoformat(),
                "student_id": record.student_id,
                "route_id": record.route_id,
                "status": record.status,
                "pickup_time": record.pickup_time or "",
                "drop_time": record.drop_time or ""
            })
        current_date += datetime.timedelta(days=1)
    
    if format == "csv":
        csv_data = generate_attendance_report_csv(all_records)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=attendance_report_{start_date}_{end_date}.csv"}
        )
    
    return {"records": all_records, "count": len(all_records)}


@router.get("/fees")
async def generate_fee_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    school_id: int = Query(...),
    format: str = Query("csv"),
    current_user=Depends(require_admin)
):
    from app.services.fee_service import get_collection_summary
    
    summary = get_collection_summary(start_date, end_date)
    
    report_data = [{
        "period": f"{start_date} to {end_date}",
        "total_collected": summary.total_collected,
        "total_transactions": summary.total_transactions,
        "online_transactions": summary.online_transactions,
        "cash_transactions": summary.cash_transactions,
        "online_amount": summary.online_amount,
        "cash_amount": summary.cash_amount
    }]
    
    if format == "csv":
        csv_data = generate_fee_report_csv(report_data)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=fee_report_{start_date}_{end_date}.csv"}
        )
    
    return summary


@router.get("/students")
async def generate_student_report(
    route_id: Optional[int] = Query(None),
    class_name: Optional[str] = Query(None),
    format: str = Query("csv"),
    current_user=Depends(get_current_user)
):
    from app.services.student_service import get_all_students
    
    students = get_all_students(route_id=route_id, class_name=class_name)
    
    report_data = [{
        "id": s.id,
        "name": f"{s.first_name} {s.last_name}",
        "email": s.email,
        "class": s.class_name,
        "section": s.section,
        "route_id": s.route_id or "",
        "status": s.status
    } for s in students]
    
    if format == "csv":
        csv_data = generate_student_list_csv(report_data)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=student_list.csv"}
        )
    
    return {"students": report_data, "count": len(report_data)}


@router.get("/vehicles")
async def generate_vehicle_report(
    status: Optional[str] = Query(None),
    format: str = Query("csv"),
    current_user=Depends(get_current_user)
):
    from app.services.vehicle_service import get_all_vehicles
    
    vehicles = get_all_vehicles(status=status)
    
    report_data = [{
        "id": v.id,
        "vehicle_number": v.vehicle_number,
        "type": v.vehicle_type,
        "capacity": v.capacity,
        "current_load": v.current_load,
        "make": v.make,
        "model": v.model,
        "year": v.year,
        "status": v.status
    } for v in vehicles]
    
    if format == "csv":
        csv_data = generate_vehicle_report_csv(report_data)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=vehicle_report.csv"}
        )
    
    return {"vehicles": report_data, "count": len(report_data)}


@router.get("/routes")
async def generate_route_report(
    format: str = Query("csv"),
    current_user=Depends(get_current_user)
):
    from app.services.route_service import get_all_routes
    
    routes = get_all_routes()
    
    report_data = [{
        "id": r.id,
        "name": r.name,
        "description": r.description or "",
        "total_distance": r.total_distance or "",
        "estimated_time": r.estimated_time or "",
        "status": r.status,
        "stops_count": len(r.stops)
    } for r in routes]
    
    if format == "csv":
        csv_data = generate_route_report_csv(report_data)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=route_report.csv"}
        )
    
    return {"routes": report_data, "count": len(report_data)}


@router.get("/monthly-attendance")
async def generate_monthly_attendance_report(
    month: int = Query(...),
    year: int = Query(...),
    current_user=Depends(get_current_user)
):
    from datetime import date as date_type
    from calendar import monthrange
    
    _, days_in_month = monthrange(year, month)
    start_date = date_type(year, month, 1)
    end_date = date_type(year, month, days_in_month)
    
    from app.services.attendance_service import get_attendance_by_date
    from collections import Counter
    
    daily_counts = {}
    current = start_date
    while current <= end_date:
        records = get_attendance_by_date(current)
        present = len([r for r in records if r.status == "present"])
        daily_counts[current.day] = present
        current += datetime.timedelta(days=1)
    
    avg_attendance = sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
    
    return {
        "month": month,
        "year": year,
        "total_school_days": len(daily_counts),
        "average_attendance": round(avg_attendance, 1),
        "daily_breakdown": daily_counts
    }
