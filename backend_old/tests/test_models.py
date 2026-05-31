import pytest
from datetime import datetime
from app.models.models import (
    User, School, Vehicle, Driver, Student, Route,
    Attendance, Fee, Payment, Notification
)

class TestModels:
    def test_user_creation(self):
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
            role="admin"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "admin"

    def test_vehicle_creation(self):
        vehicle = Vehicle(
            vehicle_number="ABC123",
            vehicle_type="bus",
            capacity=50,
            status="active"
        )
        assert vehicle.vehicle_number == "ABC123"
        assert vehicle.capacity == 50
        assert vehicle.status == "active"

    def test_driver_creation(self):
        driver = Driver(
            name="John Doe",
            phone="+1234567890",
            license_number="DL123456",
            status="active"
        )
        assert driver.name == "John Doe"
        assert driver.license_number == "DL123456"

    def test_student_creation(self):
        student = Student(
            name="Jane Doe",
            student_id="STU001",
            parent_phone="+1234567890"
        )
        assert student.name == "Jane Doe"
        assert student.student_id == "STU001"

    def test_route_creation(self):
        route = Route(
            name="Route 1",
            start_location="School",
            end_location="Home",
            distance=10.5
        )
        assert route.name == "Route 1"
        assert route.distance == 10.5

    def test_attendance_creation(self):
        attendance = Attendance(
            status="present",
            date=datetime.now()
        )
        assert attendance.status == "present"

    def test_fee_creation(self):
        fee = Fee(
            amount=1000,
            status="pending",
            due_date=datetime.now()
        )
        assert fee.amount == 1000
        assert fee.status == "pending"

    def test_notification_creation(self):
        notification = Notification(
            title="Test Notification",
            message="Test message",
            notification_type="alert"
        )
        assert notification.title == "Test Notification"
        assert notification.notification_type == "alert"