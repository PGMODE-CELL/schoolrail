import datetime as _dt
from typing import Optional, List
from pydantic import BaseModel


class AttendanceStatusEnum(str):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    ON_LEAVE = "on_leave"
    EXCUSED = "excused"


class StudentAttendanceCreate(BaseModel):
    student_id: int
    route_id: int
    status: str
    pickup_time: Optional[str] = None
    drop_time: Optional[str] = None
    notes: Optional[str] = None


class StudentAttendanceResponse(BaseModel):
    id: int
    student_id: int
    route_id: int
    attendance_date: Optional[_dt.date] = None
    status: str
    pickup_time: Optional[str] = None
    drop_time: Optional[str] = None
    marked_by: Optional[int] = None
    created_at: Optional[_dt.datetime] = None

    class Config:
        from_attributes = True


class BulkAttendanceCreate(BaseModel):
    route_id: int
    trip_date: _dt.date
    attendance_records: List[dict]


class DailyAttendanceSummary(BaseModel):
    summary_date: _dt.date
    total_students: int
    present: int
    absent: int
    late: int
    on_leave: int
    present_percentage: float


class AttendanceStatistics(BaseModel):
    total_records: int
    present: int
    absent: int
    late: int
    present_percentage: float
    absent_percentage: float
    period_days: int


class MonthlyAttendanceReport(BaseModel):
    month: str
    year: int
    total_school_days: int
    average_attendance: float
    peak_absence_date: Optional[_dt.date] = None
    by_class: List[dict]
    by_route: List[dict]


class LeaveApplication(BaseModel):
    student_id: int
    start_date: _dt.date
    end_date: _dt.date
    reason: str
    status: str = "pending"
    applied_by: int


class AttendanceFilter(BaseModel):
    route_id: Optional[int] = None
    filter_date: Optional[_dt.date] = None
    status: Optional[str] = None
    student_id: Optional[int] = None
