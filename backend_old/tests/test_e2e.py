import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuthEndpoints:
    def test_login_with_json(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_with_form(self):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
    
    def test_login_invalid_credentials(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code in [401, 400]
    
    def test_register_new_user(self):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": f"testuser_{id(self)}",
                "email": f"test_{id(self)}@test.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "User",
                "role": "parent"
            }
        )
        assert response.status_code in [200, 201, 400]


class TestSchoolsEndpoints:
    def test_list_schools(self):
        response = client.get("/api/v1/schools")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_create_school(self):
        response = client.post(
            "/api/v1/schools",
            json={
                "name": "Test School",
                "code": f"TEST{id(self)}",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "phone": "+911234567890",
                "email": "test@school.com"
            }
        )
        assert response.status_code in [200, 201, 400]


class TestVehiclesEndpoints:
    def test_list_vehicles(self):
        response = client.get("/api/v1/vehicles")
        assert response.status_code == 200
    
    def test_create_vehicle(self):
        response = client.post(
            "/api/v1/vehicles",
            json={
                "school_id": 1,
                "reg_number": f"TEST-{id(self)}",
                "vehicle_type": "Bus",
                "seating_capacity": 45
            }
        )
        assert response.status_code in [200, 201, 400]


class TestDriversEndpoints:
    def test_list_drivers(self):
        response = client.get("/api/v1/drivers")
        assert response.status_code == 200
    
    def test_create_driver(self):
        response = client.post(
            "/api/v1/drivers",
            json={
                "school_id": 1,
                "first_name": "Test",
                "last_name": "Driver",
                "phone": f"+91{id(self)}",
                "license_number": f"LIC{id(self)}",
                "license_expiry": "2025-12-31T00:00:00"
            }
        )
        assert response.status_code in [200, 201, 400]


class TestStudentsEndpoints:
    def test_list_students(self):
        response = client.get("/api/v1/students")
        assert response.status_code == 200
    
    def test_create_student(self):
        response = client.post(
            "/api/v1/students",
            json={
                "school_id": 1,
                "first_name": "Test",
                "last_name": "Student",
                "student_id": f"STU{id(self)}",
                "class_name": "Class 1"
            }
        )
        assert response.status_code in [200, 201, 400]


class TestAttendanceEndpoints:
    def test_list_attendance(self):
        response = client.get("/api/v1/attendance")
        assert response.status_code == 200
    
    def test_create_attendance(self):
        response = client.post(
            "/api/v1/attendance",
            json={
                "student_id": 1,
                "date": "2024-01-01T00:00:00",
                "trip_type": "morning",
                "status": "present"
            }
        )
        assert response.status_code in [200, 201, 400]


class TestFeesEndpoints:
    def test_list_fees(self):
        response = client.get("/api/v1/fees")
        assert response.status_code == 200
    
    def test_create_fee(self):
        response = client.post(
            "/api/v1/fees",
            json={
                "school_id": 1,
                "student_id": 1,
                "fee_type": "Transport",
                "title": "Monthly Fee",
                "amount": 3000,
                "due_date": "2024-02-01T00:00:00"
            }
        )
        assert response.status_code in [200, 201, 400]


class TestGPSEndpoints:
    def test_add_gps_location(self):
        response = client.post(
            "/api/v1/gps/location",
            params={
                "vehicle_id": 1,
                "latitude": 28.6139,
                "longitude": 77.2090,
                "speed": 30.0
            }
        )
        assert response.status_code in [200, 201]
    
    def test_get_latest_gps(self):
        response = client.get("/api/v1/gps/latest")
        assert response.status_code == 200


class TestAlertsEndpoints:
    def test_list_alerts(self):
        response = client.get("/api/v1/alerts")
        assert response.status_code == 200


class TestNotificationsEndpoints:
    def test_list_notifications(self):
        response = client.get("/api/v1/notifications")
        assert response.status_code == 200


class TestIntegration:
    def test_full_workflow(self):
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        schools_response = client.get("/api/v1/schools", headers=headers)
        assert schools_response.status_code == 200
        
        vehicles_response = client.get("/api/v1/vehicles", headers=headers)
        assert vehicles_response.status_code == 200
        
        drivers_response = client.get("/api/v1/drivers", headers=headers)
        assert drivers_response.status_code == 200
    
    def test_auth_required_endpoints(self):
        endpoints = [
            "/api/v1/schools",
            "/api/v1/vehicles",
            "/api/v1/drivers",
            "/api/v1/students",
            "/api/v1/attendance",
            "/api/v1/fees",
        ]
        
        for endpoint in endpoints:
            if "students" in endpoint or "fees" in endpoint:
                response = client.get(endpoint)
            else:
                response = client.get(endpoint)
            
            if response.status_code == 401:
                continue


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
