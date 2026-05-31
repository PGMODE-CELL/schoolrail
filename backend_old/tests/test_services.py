import pytest
from app.services.route_service import (
    get_all_routes, get_route_by_id, create_route, update_route, delete_route,
    optimize_route, add_stop_to_route
)
from app.services.student_service import (
    get_all_students, get_student_by_id, create_student, update_student, delete_student,
    get_students_by_route
)
from app.services.attendance_service import (
    get_attendance_by_date, mark_attendance, get_daily_summary,
    get_attendance_statistics, bulk_mark_attendance
)
from app.services.fee_service import (
    get_all_fee_structures, get_student_fees, create_fee_structure, record_payment
)
from app.services.notification_service import (
    get_user_notifications, create_notification, mark_notification_read,
    mark_all_read, delete_notification
)
from app.services.scan_service import (
    parse_qr_code, generate_student_qr, process_rfid_card, scan_and_mark_attendance
)
from datetime import date, timedelta
from app.schemas.route import RouteCreate, StopCreate
from app.schemas.attendance import StudentAttendanceCreate
from app.schemas.fee import FeeStructureCreate, FeePaymentCreate
from app.schemas.notification import NotificationCreate, NotificationTypeEnum


class TestRouteService:
    def test_get_all_routes(self):
        routes = get_all_routes()
        assert isinstance(routes, list)
        assert len(routes) > 0
    
    def test_get_route_by_id(self):
        route = get_route_by_id(1)
        assert route is not None
        assert route.id == 1
    
    def test_get_route_by_invalid_id(self):
        route = get_route_by_id(9999)
        assert route is None
    
    def test_optimize_route(self):
        result = optimize_route(1)
        assert result is not None
        assert "total_distance" in result or "optimized" in result


class TestStudentService:
    def test_get_all_students(self):
        students = get_all_students()
        assert isinstance(students, list)
    
    def test_get_student_by_id(self):
        student = get_student_by_id(1)
        assert student is not None
        assert student.id == 1
    
    def test_get_students_by_route(self):
        students = get_students_by_route(1)
        assert isinstance(students, list)


class TestAttendanceService:
    def test_get_daily_summary(self):
        today = date.today()
        summary = get_daily_summary(today)
        assert summary is not None
        assert hasattr(summary, 'present')
        assert hasattr(summary, 'absent')
    
    def test_get_attendance_statistics(self):
        stats = get_attendance_statistics(days=30)
        assert stats is not None
        assert hasattr(stats, 'present_percentage')


class TestFeeService:
    def test_get_all_fee_structures(self):
        structures = get_all_fee_structures()
        assert isinstance(structures, list)
        assert len(structures) > 0
    
    def test_get_student_fees(self):
        fees = get_student_fees(1)
        assert "pending" in fees
        assert "paid" in fees


class TestNotificationService:
    def test_get_user_notifications(self):
        notifications = get_user_notifications(user_id=3, user_type="parent")
        assert isinstance(notifications, list)
    
    def test_mark_notification_read(self):
        result = mark_notification_read(notification_id=1, user_id=3)
        assert result is True
    
    def test_notification_stats(self):
        stats = get_notification_stats(user_id=3, user_type="parent")
        assert "total" in stats
        assert "unread" in stats


class TestScanService:
    def test_parse_valid_qr_code(self):
        result = parse_qr_code("SR_STU:123")
        assert result["valid"] is True
        assert result["entity_type"] == "student"
        assert result["entity_id"] == 123
    
    def test_parse_invalid_qr_code(self):
        result = parse_qr_code("INVALID")
        assert result["valid"] is False
    
    def test_generate_student_qr(self):
        qr = generate_student_qr(123)
        assert qr == "SR_STU:123"
    
    def test_process_valid_rfid(self):
        result = process_rfid_card("RFID001")
        assert result["valid"] is True
        assert result["student_id"] == 1
    
    def test_process_invalid_rfid(self):
        result = process_rfid_card("INVALID123")
        assert result["valid"] is False
    
    def test_scan_and_mark_attendance_qr(self):
        result = scan_and_mark_attendance(
            scan_type="qr",
            scan_data="SR_STU:1",
            route_id=1,
            status="present"
        )
        assert result["success"] is True
    
    def test_scan_and_mark_attendance_rfid(self):
        result = scan_and_mark_attendance(
            scan_type="rfid",
            scan_data="RFID001",
            route_id=1,
            status="present"
        )
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
