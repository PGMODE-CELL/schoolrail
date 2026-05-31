"""
SchoolRail - Additional API Endpoints
=====================================
Analytics, WebSocket, and other endpoints.

Author: SchoolRail Team
License: MIT
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.utils.helpers import ResponseHelper

router = APIRouter()


@router.get("/dashboard/summary")
async def get_dashboard_summary(school_id: int = Query(...), db: Session = Depends(get_db)):
    """Get dashboard summary"""
    from app.models.models import Student, Vehicle, Driver, Route, Trip, Fee, Alert
    
    total_students = db.query(Student).filter(Student.school_id == school_id).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.school_id == school_id, Vehicle.status == "active").count()
    active_drivers = db.query(Driver).filter(Driver.school_id == school_id, Driver.status == "active").count()
    active_routes = db.query(Route).filter(Route.school_id == school_id, Route.status == "active").count()
    
    today = datetime.now().date()
    trips_today = db.query(Trip).filter(Trip.school_id == school_id, func.date(Trip.scheduled_start_time) == today).count()
    
    pending_fees = db.query(Fee).filter(Fee.school_id == school_id, Fee.status == "pending").count()
    open_alerts = db.query(Alert).filter(Alert.school_id == school_id, Alert.is_resolved == False).count()
    
    revenue = db.query(func.sum(Fee.paid_amount)).filter(Fee.school_id == school_id).scalar() or 0
    
    return ResponseHelper.success({
        "total_students": total_students,
        "active_vehicles": active_vehicles,
        "active_drivers": active_drivers,
        "active_routes": active_routes,
        "trips_today": trips_today,
        "pending_fees": pending_fees,
        "open_alerts": open_alerts,
        "revenue_month": revenue
    })


@router.get("/analytics/attendance")
async def get_attendance_analytics(school_id: int = Query(...), days: int = Query(30), db: Session = Depends(get_db)):
    """Get attendance analytics"""
    from app.models.models import Attendance, Student
    
    start_date = datetime.now() - timedelta(days=days)
    
    attendances = db.query(Attendance).join(Student).filter(
        Student.school_id == school_id,
        Attendance.date >= start_date
    ).all()
    
    total = len(attendances)
    present = sum(1 for a in attendances if a.status == "present")
    absent = sum(1 for a in attendances if a.status == "absent")
    late = sum(1 for a in attendances if a.status == "late")
    
    return ResponseHelper.success({
        "total": total,
        "present": present,
        "absent": absent,
        "late": late,
        "percentage": round((present / total * 100), 2) if total > 0 else 0
    })


@router.get("/analytics/fees")
async def get_fees_analytics(school_id: int = Query(...), db: Session = Depends(get_db)):
    """Get fees analytics"""
    from app.models.models import Fee
    
    total_generated = db.query(func.sum(Fee.final_amount)).filter(Fee.school_id == school_id).scalar() or 0
    total_collected = db.query(func.sum(Fee.paid_amount)).filter(Fee.school_id == school_id).scalar() or 0
    pending_count = db.query(Fee).filter(Fee.school_id == school_id, Fee.status == "pending").count()
    
    return ResponseHelper.success({
        "total_generated": total_generated,
        "total_collected": total_collected,
        "total_pending": total_generated - total_collected,
        "pending_count": pending_count,
        "collection_rate": round((total_collected / total_generated * 100), 2) if total_generated > 0 else 0
    })


@router.get("/analytics/vehicles")
async def get_vehicle_analytics(school_id: int = Query(...), db: Session = Depends(get_db)):
    """Get vehicle analytics"""
    from app.models.models import Vehicle
    
    total = db.query(Vehicle).filter(Vehicle.school_id == school_id).count()
    active = db.query(Vehicle).filter(Vehicle.school_id == school_id, Vehicle.status == "active").count()
    maintenance = db.query(Vehicle).filter(Vehicle.school_id == school_id, Vehicle.status == "maintenance").count()
    
    return ResponseHelper.success({
        "total": total,
        "active": active,
        "maintenance": maintenance,
        "idle": total - active - maintenance,
        "utilization": round((active / total * 100), 2) if total > 0 else 0
    })


@router.get("/analytics/routes")
async def get_route_analytics(school_id: int = Query(...), db: Session = Depends(get_db)):
    """Get route analytics"""
    from app.models.models import Route, Stop, Student
    
    routes = db.query(Route).filter(Route.school_id == school_id).all()
    
    data = []
    for route in routes:
        stops_count = db.query(Stop).filter(Stop.route_id == route.id).count()
        students_count = db.query(Student).filter(Student.route_id == route.id).count()
        
        data.append({
            "id": route.id,
            "name": route.name,
            "code": route.route_code,
            "stops": stops_count,
            "students": students_count,
            "distance": route.total_distance_km,
            "duration": route.estimated_time_minutes
        })
    
    return ResponseHelper.success(data)


@router.post("/notifications/send")
async def send_notification(recipient: str, message: str, notification_type: str = "sms", db: Session = Depends(get_db)):
    """Send notification (placeholder)"""
    return ResponseHelper.success({"status": "sent"}, "Notification sent")


@router.get("/health/check")
async def health_check():
    """Health check endpoint"""
    return ResponseHelper.success({"status": "healthy", "timestamp": datetime.now().isoformat()})


@router.get("/reports/export")
async def export_report(report_type: str, school_id: int, format: str = "json", db: Session = Depends(get_db)):
    """Export report"""
    return ResponseHelper.success({"message": f"{report_type} report ready for export"})


@router.post("/gps/update")
async def update_gps(vehicle_id: int, latitude: float, longitude: float, speed: Optional[float] = 0, db: Session = Depends(get_db)):
    """Update GPS location"""
    from app.models.models import GPSLocation
    
    location = GPSLocation(vehicle_id=vehicle_id, latitude=latitude, longitude=longitude, speed_kmh=speed)
    db.add(location)
    db.commit()
    
    return ResponseHelper.success({"message": "GPS updated"})


@router.get("/trips/current")
async def get_current_trip(school_id: int = Query(...), db: Session = Depends(get_db)):
    """Get current trip"""
    from app.models.models import Trip
    
    today = datetime.now().date()
    trip = db.query(Trip).filter(
        Trip.school_id == school_id,
        func.date(Trip.scheduled_start_time) == today,
        Trip.status == "ongoing"
    ).first()
    
    if trip:
        return ResponseHelper.success({
            "id": trip.id,
            "status": trip.status,
            "start_time": trip.scheduled_start_time.isoformat() if trip.scheduled_start_time else None
        })
    
    return ResponseHelper.success(None, "No active trip")


@router.post("/attendance/mark")
async def mark_attendance(student_id: int, status: str, trip_type: str, date: str = None, db: Session = Depends(get_db)):
    """Mark student attendance"""
    from app.models.models import Attendance
    
    if not date:
        date = datetime.now()
    else:
        date = datetime.fromisoformat(date)
    
    attendance = Attendance(student_id=student_id, date=date, trip_type=trip_type, status=status)
    db.add(attendance)
    db.commit()
    
    return ResponseHelper.success({"id": attendance.id}, "Attendance marked")


@router.get("/alerts/active")
async def get_active_alerts(school_id: int = Query(...), db: Session = Depends(get_db)):
    """Get active alerts"""
    from app.models.models import Alert
    
    alerts = db.query(Alert).filter(
        Alert.school_id == school_id,
        Alert.is_resolved == False
    ).order_by(Alert.created_at.desc()).limit(20).all()
    
    return ResponseHelper.success([{
        "id": a.id,
        "title": a.title,
        "message": a.message,
        "type": a.alert_type,
        "created_at": a.created_at.isoformat()
    } for a in alerts])


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, notes: str = None, db: Session = Depends(get_db)):
    """Resolve alert"""
    from app.models.models import Alert
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_resolved = True
        alert.resolution_notes = notes
        alert.resolved_at = datetime.now()
        db.commit()
    
    return ResponseHelper.success({"message": "Alert resolved"})


@router.get("/maintenance/upcoming")
async def get_upcoming_maintenance(school_id: int = Query(...), days: int = Query(7), db: Session = Depends(get_db)):
    """Get upcoming maintenance"""
    from app.models.models import Vehicle
    
    vehicles = db.query(Vehicle).filter(Vehicle.school_id == school_id).all()
    
    upcoming = []
    for v in vehicles:
        if v.next_service_date and v.next_service_date <= datetime.now() + timedelta(days=days):
            upcoming.append({
                "vehicle_id": v.id,
                "reg_number": v.reg_number,
                "service_date": v.next_service_date.isoformat()
            })
    
    return ResponseHelper.success(upcoming)


@router.get("/stops/route/{route_id}")
async def get_stops_by_route(route_id: int, db: Session = Depends(get_db)):
    """Get stops for a route"""
    from app.models.models import Stop
    
    stops = db.query(Stop).filter(Stop.route_id == route_id).order_by(Stop.stop_order).all()
    
    return ResponseHelper.success([{
        "id": s.id,
        "name": s.name,
        "order": s.stop_order,
        "latitude": s.latitude,
        "longitude": s.longitude,
        "time": s.estimated_arrival_time
    } for s in stops])


@router.get("/students/route/{route_id}")
async def get_students_by_route(route_id: int, db: Session = Depends(get_db)):
    """Get students by route"""
    from app.models.models import Student
    
    students = db.query(Student).filter(Student.route_id == route_id, Student.status == "active").all()
    
    return ResponseHelper.success([{
        "id": s.id,
        "name": s.full_name,
        "class": s.class_name,
        "stop": s.pickup_stop_id
    } for s in students])


@router.post("/fee/create")
async def create_fee(school_id: int, student_id: int, title: str, amount: float, due_date: str, db: Session = Depends(get_db)):
    """Create fee"""
    from app.models.models import Fee
    
    fee = Fee(school_id=school_id, student_id=student_id, fee_type="Transport Fee", title=title,
             amount=amount, total_amount=amount, final_amount=amount, due_date=datetime.fromisoformat(due_date),
             status="pending")
    db.add(fee)
    db.commit()
    
    return ResponseHelper.success({"id": fee.id}, "Fee created")


@router.post("/payment/process")
async def process_payment(fee_id: int, amount: float, method: str = "online", db: Session = Depends(get_db)):
    """Process payment"""
    from app.models.models import Fee, Payment
    
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if fee:
        fee.paid_amount += amount
        fee.status = "paid" if fee.paid_amount >= fee.final_amount else "partial"
        fee.paid_date = datetime.now()
        fee.payment_method = method
        
        payment = Payment(fee_id=fee_id, student_id=fee.student_id, amount=amount,
                        payment_method=method, payment_date=datetime.now(), status="success")
        db.add(payment)
        db.commit()
    
    return ResponseHelper.success({"message": "Payment processed"})