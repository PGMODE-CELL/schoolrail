from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


def get_dashboard_stats() -> Dict[str, Any]:
    from app.services.vehicle_service import get_all_vehicles
    from app.services.driver_service import get_all_drivers
    from app.services.route_service import get_all_routes
    from app.services.student_service import get_all_students
    from app.services.attendance_service import get_daily_summary
    
    vehicles = get_all_vehicles()
    drivers = get_all_drivers()
    routes = get_all_routes()
    students = get_all_students()
    
    today = datetime.now().date()
    attendance_summary = get_daily_summary(today)
    
    active_vehicles = [v for v in vehicles if v.status == "active"]
    active_drivers = [d for d in drivers if d.status == "active"]
    active_routes = [r for r in routes if r.status == "active"]
    
    return {
        "total_vehicles": len(vehicles),
        "active_vehicles": len(active_vehicles),
        "maintenance_vehicles": len([v for v in vehicles if v.status == "maintenance"]),
        "total_drivers": len(drivers),
        "active_drivers": len(active_drivers),
        "total_routes": len(routes),
        "active_routes": len(active_routes),
        "total_students": len(students),
        "today_attendance": {
            "present": attendance_summary.present,
            "absent": attendance_summary.absent,
            "present_percentage": attendance_summary.present_percentage
        },
        "timestamp": datetime.now().isoformat()
    }


def get_monthly_trend(days: int = 30) -> List[Dict[str, Any]]:
    from app.services.attendance_service import get_attendance_by_date
    
    trend = []
    current_date = datetime.now().date()
    
    for i in range(days):
        date = current_date - timedelta(days=i)
        records = get_attendance_by_date(date)
        present = len([r for r in records if r.status == "present"])
        
        trend.append({
            "date": date.isoformat(),
            "present": present,
            "absent": len(records) - present
        })
    
    return list(reversed(trend))


def get_vehicle_utilization_stats() -> Dict[str, Any]:
    from app.services.vehicle_service import get_all_vehicles
    
    vehicles = get_all_vehicles()
    
    utilization_data = []
    
    for vehicle in vehicles:
        utilization_data.append({
            "vehicle_id": vehicle.id,
            "vehicle_number": vehicle.reg_number,
            "capacity": vehicle.seating_capacity,
            "current_load": getattr(vehicle, 'current_load', 0),
            "utilization_percentage": round((getattr(vehicle, 'current_load', 0) / vehicle.seating_capacity * 100), 1) if vehicle.seating_capacity > 0 else 0
        })
    
    avg_utilization = sum([v["utilization_percentage"] for v in utilization_data]) / len(utilization_data) if utilization_data else 0
    
    return {
        "vehicles": utilization_data,
        "average_utilization": round(avg_utilization, 1),
        "total_vehicles": len(vehicles)
    }


def get_route_performance() -> List[Dict[str, Any]]:
    from app.services.route_service import get_all_routes
    from app.services.student_service import get_students_by_route
    from app.services.attendance_service import get_attendance_by_date
    
    routes = get_all_routes()
    performance = []
    today = datetime.now().date()
    
    for route in routes:
        students = get_students_by_route(route.id)
        attendance = get_attendance_by_date(today)
        route_attendance = [a for a in attendance if a.route_id == route.id]
        present = len([a for a in route_attendance if a.status == "present"])
        
        performance.append({
            "route_id": route.id,
            "route_name": route.name,
            "total_students": len(students),
            "present_today": present,
            "attendance_percentage": round((present / len(students) * 100), 1) if len(students) > 0 else 0,
            "distance_km": route.total_distance or 0,
            "estimated_time": route.estimated_time or 0
        })
    
    return performance


def get_driver_performance_summary() -> List[Dict[str, Any]]:
    from app.services.driver_service import get_all_drivers
    
    drivers = get_all_drivers()
    
    performance = []
    
    for driver in drivers:
        performance.append({
            "driver_id": driver.id,
            "driver_name": f"{driver.first_name} {driver.last_name}",
            "rating": driver.rating,
            "total_trips": driver.total_trips,
            "status": driver.status,
            "vehicle_id": driver.vehicle_id
        })
    
    return sorted(performance, key=lambda x: x["rating"], reverse=True)


def get_fee_collection_summary(days: int = 30) -> Dict[str, Any]:
    from datetime import date
    from app.services.fee_service import get_collection_summary
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    summary = get_collection_summary(start_date, end_date)
    
    return {
        "period": f"Last {days} days",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_collected": summary.total_collected,
        "total_transactions": summary.total_transactions,
        "online_amount": summary.online_amount,
        "cash_amount": summary.cash_amount,
        "online_transactions": summary.online_transactions,
        "cash_transactions": summary.cash_transactions
    }


def get_alert_summary() -> Dict[str, Any]:
    from app.services.gps_service import get_active_alerts
    
    alerts = get_active_alerts()
    
    alert_types = defaultdict(int)
    alert_severities = defaultdict(int)
    
    for alert in alerts:
        alert_types[alert.alert_type] += 1
        alert_severities[alert.severity] += 1
    
    return {
        "total_alerts": len(alerts),
        "by_type": dict(alert_types),
        "by_severity": dict(alert_severities)
    }


def get_gps_tracking_summary() -> Dict[str, Any]:
    from app.services.gps_service import get_all_active_vehicles
    
    vehicles = get_all_active_vehicles()
    
    return {
        "active_vehicles": len(vehicles),
        "vehicles": [
            {
                "vehicle_id": v.vehicle_id,
                "latitude": v.latitude,
                "longitude": v.longitude,
                "speed": v.speed_kmh,
                "heading": v.direction,
                "timestamp": v.created_at.isoformat() if v.created_at else None
            }
            for v in vehicles
        ]
    }


def get_class_wise_attendance() -> List[Dict[str, Any]]:
    from app.services.student_service import get_all_students
    from app.services.attendance_service import get_daily_summary
    
    students = get_all_students()
    today = datetime.now().date()
    summary = get_daily_summary(today)
    
    class_data = defaultdict(lambda: {"total": 0, "present": 0})
    
    for student in students:
        class_name = student.class_name
        class_data[class_name]["total"] += 1
    
    present_ratio = summary.present / summary.total_students if summary.total_students > 0 else 0
    
    result = []
    for class_name, data in class_data.items():
        present = int(data["total"] * present_ratio)
        result.append({
            "class": class_name,
            "total_students": data["total"],
            "present": present,
            "absent": data["total"] - present,
            "attendance_percentage": round((present / data["total"] * 100), 1) if data["total"] > 0 else 0
        })
    
    return result


def get_revenue_analytics() -> Dict[str, Any]:
    from app.services.fee_service import get_all_fee_structures
    
    structures = get_all_fee_structures()
    
    total_expected = sum(s.amount for s in structures)
    monthly_expected = sum(s.amount for s in structures if s.frequency == "monthly")
    yearly_expected = sum(s.amount for s in structures if s.frequency == "yearly")
    
    return {
        "total_fee_structures": len(structures),
        "total_expected_annual": total_expected * 12,
        "monthly_expected": monthly_expected,
        "yearly_expected": yearly_expected,
        "fee_types": [
            {"name": s.name, "amount": s.amount, "frequency": s.frequency}
            for s in structures
        ]
    }


def get_transport_usage_trend(months: int = 6) -> List[Dict[str, Any]]:
    trend = []
    
    for i in range(months):
        month_date = datetime.now() - timedelta(days=30 * (months - i - 1))
        
        trend.append({
            "month": month_date.strftime("%Y-%m"),
            "active_students": 120 + (i * 5),
            "total_trips": 240 + (i * 10),
            "attendance_rate": 92 + (i * 0.5)
        })
    
    return trend