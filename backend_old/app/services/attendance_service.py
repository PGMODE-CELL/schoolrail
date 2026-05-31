from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.models import Attendance
from app.schemas.attendance import (
    StudentAttendanceCreate,
    StudentAttendanceResponse,
    DailyAttendanceSummary,
    AttendanceStatistics
)


def _attendance_to_dict(att: Attendance) -> dict:
    return {
        "id": att.id,
        "student_id": att.student_id,
        "route_id": att.trip_id,
        "attendance_date": att.date.date() if isinstance(att.date, datetime) else att.date,
        "status": att.status,
        "pickup_time": att.scheduled_time if att.trip_type == "morning_pickup" else None,
        "drop_time": att.scheduled_time if att.trip_type == "evening_drop" else None,
        "marked_by": att.source,
        "created_at": att.created_at,
    }


def get_attendance_by_date(attendance_date: date) -> List[StudentAttendanceResponse]:
    db = SessionLocal()
    try:
        attendances = db.query(Attendance).filter(
            func.date(Attendance.date) == attendance_date
        ).all()
        return [StudentAttendanceResponse(**_attendance_to_dict(a)) for a in attendances]
    except Exception:
        return []
    finally:
        db.close()


def get_student_attendance(student_id: int, start_date: date, end_date: date) -> List[StudentAttendanceResponse]:
    db = SessionLocal()
    try:
        attendances = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            func.date(Attendance.date) >= start_date,
            func.date(Attendance.date) <= end_date
        ).all()
        return [StudentAttendanceResponse(**_attendance_to_dict(a)) for a in attendances]
    except Exception:
        return []
    finally:
        db.close()


def mark_attendance(attendance_data: StudentAttendanceCreate) -> StudentAttendanceResponse:
    db = SessionLocal()
    try:
        data = attendance_data.model_dump()
        attendance = Attendance(
            student_id=data.get("student_id"),
            trip_id=data.get("route_id"),
            date=datetime.combine(datetime.now().date(), datetime.min.time()),
            trip_type="morning_pickup" if data.get("status") == "present" else "evening_drop",
            status=data.get("status"),
            scheduled_time=data.get("pickup_time") or data.get("drop_time"),
            source="manual",
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return StudentAttendanceResponse(**_attendance_to_dict(attendance))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_daily_summary(attendance_date: date) -> DailyAttendanceSummary:
    db = SessionLocal()
    try:
        attendances = db.query(Attendance).filter(
            func.date(Attendance.date) == attendance_date
        ).all()
        present = len([a for a in attendances if a.status == "present"])
        absent = len([a for a in attendances if a.status == "absent"])
        late = len([a for a in attendances if a.status == "late"])
        total = len(attendances)

        return DailyAttendanceSummary(
            summary_date=attendance_date,
            total_students=total if total > 0 else 150,
            present=present,
            absent=absent,
            late=late,
            on_leave=(total if total > 0 else 150) - present - absent - late,
            present_percentage=round(present / total * 100, 1) if total > 0 else 0
        )
    except Exception:
        return DailyAttendanceSummary(
            summary_date=attendance_date,
            total_students=0,
            present=0,
            absent=0,
            late=0,
            on_leave=0,
            present_percentage=0.0
        )
    finally:
        db.close()


def get_attendance_statistics(student_id: Optional[int] = None, days: int = 30) -> AttendanceStatistics:
    db = SessionLocal()
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        query = db.query(Attendance).filter(
            func.date(Attendance.date) >= start_date,
            func.date(Attendance.date) <= end_date
        )
        if student_id:
            query = query.filter(Attendance.student_id == student_id)

        attendances = query.all()
        present = len([a for a in attendances if a.status == "present"])
        absent = len([a for a in attendances if a.status == "absent"])
        late = len([a for a in attendances if a.status == "late"])
        total = len(attendances)

        return AttendanceStatistics(
            total_records=total,
            present=present,
            absent=absent,
            late=late,
            present_percentage=round(present / total * 100, 1) if total > 0 else 0,
            absent_percentage=round(absent / total * 100, 1) if total > 0 else 0,
            period_days=days
        )
    except Exception:
        return AttendanceStatistics(
            total_records=0,
            present=0,
            absent=0,
            late=0,
            present_percentage=0.0,
            absent_percentage=0.0,
            period_days=days
        )
    finally:
        db.close()


def bulk_mark_attendance(student_ids: List[int], status: str, attendance_date: date, driver_id: int) -> dict:
    db = SessionLocal()
    try:
        marked_count = 0
        for student_id in student_ids:
            existing = db.query(Attendance).filter(
                Attendance.student_id == student_id,
                func.date(Attendance.date) == attendance_date
            ).first()
            if existing:
                existing.status = status
                marked_count += 1
            else:
                attendance = Attendance(
                    student_id=student_id,
                    date=datetime.combine(attendance_date, datetime.min.time()),
                    trip_type="morning_pickup" if status == "present" else "evening_drop",
                    status=status,
                    scheduled_time=datetime.now().strftime("%I:%M %p") if status == "present" else None,
                    source="manual",
                )
                db.add(attendance)
                marked_count += 1
        db.commit()
        return {"marked_count": marked_count, "total": len(student_ids)}
    except Exception:
        db.rollback()
        return {"marked_count": 0, "total": len(student_ids)}
    finally:
        db.close()
