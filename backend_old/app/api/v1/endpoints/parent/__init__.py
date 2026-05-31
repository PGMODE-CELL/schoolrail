from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.security import get_current_user, UserInDB

router = APIRouter(prefix="/parent", tags=["Parent App"])


class ParentStudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    class_name: str
    section: str
    route_id: Optional[int] = None
    route_name: Optional[str] = None
    bus_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None


class ChildOverviewResponse(BaseModel):
    student: ParentStudentResponse
    today_status: str
    next_bus_arrival: Optional[str] = None
    pending_fees: int
    unread_notifications: int


@router.get("/students", response_model=List[ParentStudentResponse])
async def get_parent_students(current_user: UserInDB = Depends(get_current_user)):
    from app.services.student_service import get_all_students
    from app.services.route_service import get_route_by_id
    from app.services.vehicle_service import get_vehicle_by_id
    from app.services.driver_service import get_driver_by_id
    
    students = get_all_students()
    parent_students = [s for s in students][:2]
    
    result = []
    for student in parent_students:
        route = get_route_by_id(student.route_id) if student.route_id else None
        vehicle = get_vehicle_by_id(route.vehicle_id) if route and route.vehicle_id else None
        driver = get_driver_by_id(route.driver_id) if route and route.driver_id else None
        
        result.append(ParentStudentResponse(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name or "",
            full_name=student.first_name + " " + (student.last_name or ""),
            class_name=student.class_name,
            section=student.section or "",
            route_id=route.id if route else None,
            route_name=route.name if route else None,
            bus_number=vehicle.reg_number if vehicle else None,
            driver_name=(driver.first_name + " " + driver.last_name) if driver else None,
            driver_phone=driver.phone if driver else None
        ))
    
    return result


@router.get("/students/{student_id}/overview")
async def get_child_overview(
    student_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.student_service import get_student_by_id
    from app.services.attendance_service import get_student_attendance
    from app.services.fee_service import get_student_fees
    from app.services.notification_service import get_user_notifications
    from app.services.route_service import get_route_by_id
    
    student = get_student_by_id(student_id)
    if not student:
        return {"error": "Student not found"}
    
    today = datetime.now().date()
    start_date = today
    end_date = today
    attendance = get_student_attendance(student_id, start_date, end_date)
    
    fees = get_student_fees(student_id)
    pending_count = len(fees.get("pending", []))
    
    notifications = get_user_notifications(user_id=str(student_id), unread_only=True)
    
    route = get_route_by_id(student.route_id) if student.route_id else None
    
    return {
        "student": {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "class_name": student.class_name,
            "section": student.section,
            "route_name": route.name if route else None
        },
        "today_status": attendance[0].status if attendance else "not_marked",
        "next_bus_arrival": "15 minutes" if route else None,
        "pending_fees": pending_count,
        "unread_notifications": len(notifications)
    }


@router.get("/students/{student_id}/live-location")
async def get_child_live_location(
    student_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.student_service import get_student_by_id
    from app.services.route_service import get_route_by_id
    from app.services.gps_service import get_vehicle_location
    
    student = get_student_by_id(student_id)
    if not student:
        return {"error": "Student not found"}
    
    route = get_route_by_id(student.route_id) if student.route_id else None
    if not route or not route.vehicle_id:
        return {"error": "No route assigned"}
    
    location = get_vehicle_location(route.vehicle_id)
    if not location:
        return {"error": "No location data available", "is_active": False}
    
    return {
        "is_active": True,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "speed": location.speed,
        "heading": location.heading,
        "timestamp": location.timestamp.isoformat() if location.timestamp else None,
        "bus_number": None,
        "eta_minutes": 15
    }


@router.get("/students/{student_id}/bus-eta")
async def get_bus_eta(
    student_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.services.student_service import get_student_by_id
    from app.services.route_service import get_route_by_id
    
    student = get_student_by_id(student_id)
    if not student or not student.route_id:
        return {"eta_minutes": None, "message": "No route assigned"}
    
    route = get_route_by_id(student.route_id)
    if not route:
        return {"eta_minutes": None, "message": "Route not found"}
    
    return {
        "eta_minutes": route.estimated_time or 30,
        "distance_km": route.total_distance or 0,
        "stop_name": "Your stop",
        "bus_status": "on_time"
    }


@router.get("/help/topics")
async def get_help_topics():
    return {
        "topics": [
            {"id": 1, "title": "How to track my child?", "category": "tracking"},
            {"id": 2, "title": "How to view attendance?", "category": "attendance"},
            {"id": 3, "title": "How to pay fees?", "category": "fees"},
            {"id": 4, "title": "How to contact driver?", "category": "contact"},
            {"id": 5, "title": "What if bus is late?", "category": "general"},
            {"id": 6, "title": "How to update profile?", "category": "profile"},
        ]
    }


@router.get("/help/topics/{topic_id}")
async def get_help_topic_content(topic_id: int):
    content_map = {
        1: {
            "title": "How to track my child?",
            "content": "To track your child in real-time: 1. Open the app and go to Home. 2. Tap on 'Live Track' for your child. 3. You can see the bus location on the map with ETA.",
            "related_topics": [2, 5]
        },
        2: {
            "title": "How to view attendance?",
            "content": "To view attendance: 1. Go to Attendance tab. 2. Select the date range. 3. View your child's attendance records with status (present/absent/late).",
            "related_topics": [1]
        },
        3: {
            "title": "How to pay fees?",
            "content": "To pay fees: 1. Go to Fees tab. 2. View pending fees. 3. Tap 'Pay Now'. 4. Complete payment via card/UPI/net banking. 5. Get instant receipt.",
            "related_topics": []
        },
        4: {
            "title": "How to contact driver?",
            "content": "To contact the driver: 1. Go to your child's route details. 2. Tap on driver info. 3. Use the call button to directly call the driver.",
            "related_topics": [5]
        },
        5: {
            "title": "What if bus is late?",
            "content": "If the bus is running late: 1. You'll receive a push notification. 2. Check the live tracking for updated ETA. 3. Contact school transport for more info.",
            "related_topics": [1, 4]
        },
        6: {
            "title": "How to update profile?",
            "content": "To update your profile: 1. Go to Profile tab. 2. Tap 'Edit Profile'. 3. Update your details. 4. Save changes.",
            "related_topics": []
        }
    }
    
    return content_map.get(topic_id, {"title": "Not found", "content": "Topic not found"})
